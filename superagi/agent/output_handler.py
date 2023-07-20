from superagi.agent.common_types import TaskExecutorResponse, ToolExecutorResponse
from superagi.agent.output_parser import AgentSchemaOutputParser
from superagi.agent.task_queue import TaskQueue
from superagi.agent.tool_executor import ToolExecutor
from superagi.helper.json_cleaner import JsonCleaner
from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.agent_execution_feed import AgentExecutionFeed
import numpy as np

from superagi.models.agent_execution_permission import AgentExecutionPermission


class ToolOutputHandler:
    def __init__(self, agent_execution_id: int, agent_config: dict, tools: list):
        self.agent_execution_id = agent_execution_id
        self.task_queue = TaskQueue(str(agent_execution_id))
        self.agent_config = agent_config
        self.tools = tools

    def handle(self, session, assistant_reply):
        response = self.check_permission_in_restricted_mode(session, assistant_reply)
        if response.is_permission_required:
            return response

        tool_response = self.handle_tool_response(session, assistant_reply)

        agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_execution_id,
                                                  agent_id=self.agent_config["agent_id"],
                                                  feed=assistant_reply,
                                                  role="assistant")
        session.add(agent_execution_feed)
        tool_response_feed = AgentExecutionFeed(agent_execution_id=self.agent_execution_id,
                                                agent_id=self.agent_config["agent_id"],
                                                feed=tool_response.result,
                                                role="system")
        session.add(tool_response_feed)
        session.commit()
        if not tool_response.retry:
            tool_response = self.check_for_completion(tool_response)

        return tool_response

    def handle_tool_response(self, session, assistant_reply):
        output_parser = AgentSchemaOutputParser()
        action = output_parser.parse(assistant_reply)
        agent = session.query(Agent).filter(Agent.id == self.agent_config["agent_id"]).first()
        organisation = agent.get_agent_organisation(session)
        tool_executor = ToolExecutor(organisation_id=organisation.id, agent_id=agent.id, tools=self.tools)
        return tool_executor.execute(session, action.name, action.args)

    def check_permission_in_restricted_mode(self, session, assistant_reply: str):
        action = AgentSchemaOutputParser().parse(assistant_reply)
        tools = {t.name: t for t in self.tools}

        excluded_tools = [ToolExecutor.FINISH, '', None]

        if self.agent_config["permission_type"].upper() == "RESTRICTED" and action.name not in excluded_tools and \
                tools.get(action.name) and tools[action.name].permission_required:
            new_agent_execution_permission = AgentExecutionPermission(
                agent_execution_id=self.agent_config["agent_execution_id"],
                status="PENDING",
                agent_id=self.agent_config["agent_id"],
                tool_name=action.name,
                assistant_reply=assistant_reply)

            session.add(new_agent_execution_permission)
            session.commit()
            return ToolExecutorResponse(is_permission_required=True, status="WAITING_FOR_PERMISSION",
                                        permission_id=new_agent_execution_permission.id)
        return ToolExecutorResponse(status="PENDING", is_permission_required=False)

    def check_for_completion(self, tool_response):
        self.task_queue.complete_task(tool_response.result)
        current_tasks = self.task_queue.get_tasks()
        if self.task_queue.get_completed_tasks() and len(current_tasks) == 0:
            tool_response.status = "COMPLETE"
        if current_tasks and tool_response.status == "COMPLETE":
            tool_response.status = "PENDING"
        return tool_response


class TaskOutputHandler:
    """This class handles the task output type.
    LLM output is mostly in the array of tasks and handler adds every task to the task queue.
    """

    def __init__(self, agent_execution_id: int, agent_config: dict):
        self.task_queue = TaskQueue(str(agent_execution_id))
        self.agent_config = agent_config

    def handle(self, session, assistant_reply):
        assistant_reply = JsonCleaner.extract_json_array_section(assistant_reply)
        tasks = eval(assistant_reply)
        tasks = np.array(tasks).flatten().tolist()
        for task in reversed(tasks):
            self.task_queue.add_task(task)
        if len(tasks) > 0:
            logger.info("Adding task to queue: " + str(tasks))
        for task in tasks:
            agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                      agent_id=self.agent_config["agent_id"],
                                                      feed="New Task Added: " + task,
                                                      role="system")
            session.add(agent_execution_feed)
        status = "COMPLETE" if len(self.task_queue.get_tasks()) == 0 else "PENDING"
        session.commit()
        return TaskExecutorResponse(status=status, retry=False)


class ReplaceTaskOutputHandler:
    """This class handles the replace/prioritze task output type.
    LLM output is mostly in the array of tasks and handler adds every task to the task queue.
    """

    def __init__(self, agent_execution_id: int, agent_config: dict):
        self.task_queue = TaskQueue(str(agent_execution_id))
        self.agent_config = agent_config

    def handle(self, session, assistant_reply):
        assistant_reply = JsonCleaner.extract_json_array_section(assistant_reply)
        tasks = eval(assistant_reply)
        self.task_queue.clear_tasks()
        for task in reversed(tasks):
            self.task_queue.add_task(task)
        if len(tasks) > 0:
            logger.info("Tasks reprioritized in order: " + str(tasks))
        status = "COMPLETE" if len(self.task_queue.get_tasks()) == 0 else "PENDING"
        session.commit()
        return TaskExecutorResponse(status=status, retry=False)


def get_output_handler(output_type: str, agent_execution_id: int, agent_config: dict, agent_tools: list = []):
    if output_type == "tools":
        return ToolOutputHandler(agent_execution_id, agent_config, agent_tools)
    elif output_type == "replace_tasks":
        return ReplaceTaskOutputHandler(agent_execution_id, agent_config)
    elif output_type == "tasks":
        return TaskOutputHandler(agent_execution_id, agent_config)
    return ToolOutputHandler(agent_execution_id, agent_config, agent_tools)
