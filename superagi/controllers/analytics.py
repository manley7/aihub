from fastapi import APIRouter, Depends, HTTPException
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.apm.analytics_helper import AnalyticsHelper
from superagi.apm.event_handler import EventHandler
from superagi.apm.tools_handler import ToolsHandler
from superagi.apm.knowledge_handler import KnowledgeHandler
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
import logging

router = APIRouter()

@router.get("/metrics", status_code=200)
def get_metrics(organisation=Depends(get_user_organisation)):
    """
    Get the total tokens, total calls, and the number of run completed.

    Returns:
        metrics: dictionary containing total tokens, total calls, and the number of runs completed.

    """
    try:
        return AnalyticsHelper(session=db.session, organisation_id=organisation.id).calculate_run_completed_metrics()
    except Exception as e:
        logging.error(f"Error while calculating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/agents/all", status_code=200)
def get_agents(organisation=Depends(get_user_organisation)):
    try:
        return AnalyticsHelper(session=db.session, organisation_id=organisation.id).fetch_agent_data()
    except Exception as e:
        logging.error(f"Error while fetching agent data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/agents/{agent_id}", status_code=200)
def get_agent_runs(agent_id: int, organisation=Depends(get_user_organisation)):
    try:
        return AnalyticsHelper(session=db.session, organisation_id=organisation.id).fetch_agent_runs(agent_id)
    except Exception as e:
        logging.error(f"Error while fetching agent runs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/runs/active", status_code=200)
def get_active_runs(organisation=Depends(get_user_organisation)):
    try:
        return AnalyticsHelper(session=db.session, organisation_id=organisation.id).get_active_runs()
    except Exception as e:
        logging.error(f"Error while getting active runs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/tools/used", status_code=200)
def get_tools_used(organisation=Depends(get_user_organisation)):
    try:
        return ToolsHandler(session=db.session, organisation_id=organisation.id).calculate_tool_usage()
    except Exception as e:
        logging.error(f"Error while calculating tool usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/tools/usage", status_code=200)
def get_tool_usage(organisation=Depends(get_user_organisation)):
    try: 
        return ToolsHandler(session=db.session, organisation_id=organisation.id).get_tool_wise_usage()
    except Exception as e:
        logging.error(f"Error while getting the tools' usage details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/knowledge/usage", status_code=200)
def get_knowledge_usage(organisation=Depends(get_user_organisation)):
    try: 
        return KnowledgeHandler(session=db.session, organisation_id=organisation.id).get_knowledge_wise_usage()
    except Exception as e:
        logging.error(f"Error while getting the knowledge usage details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/tools/{tool_name}/logs", status_code=200)
def get_tool_logs(tool_name: str, organisation=Depends(get_user_organisation)):
    try: 
        return ToolsHandler(session=db.session, organisation_id=organisation.id).get_tool_logs_by_tool_name(tool_name)
    except Exception as e:
        logging.error(f"Error while getting tool log details: {str(e)}")
        if e.status_code:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")    

@router.get("/knowledge/{knowledge_name}/logs", status_code=200)
def get_knowledge_logs(knowledge_name: str, organisation=Depends(get_user_organisation)):
    try: 
        return KnowledgeHandler(session=db.session, organisation_id=organisation.id).get_knowledge_logs_by_name(knowledge_name)
    except Exception as e:
        logging.error(f"Error while getting tool log details: {str(e)}")
        if e.status_code:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")