import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";

export default function RunHistory({runs, setHistory}) {
  const [selectedRun, setSelectedRun] = useState(runs[runs.length - 1].id)

  function convertToMinutes(seconds) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}`;
  }

  return (<>
    <div style={{width:'20%',height:'100%'}}>
      <div className={styles.detail_top}>
        <div style={{display:'flex'}}>
          <div style={{display:'flex',alignItems:'center',paddingLeft:'0'}} className={styles.tab_text}>
            <div>
              <Image width={16} height={16} src="/images/update.png" alt="update-icon"/>
            </div>
            <div style={{marginLeft:'7px'}}>Run history</div>
          </div>
        </div>
        <div style={{display:'flex'}}>
          <div style={{display:'flex',alignItems:'center',cursor:'pointer'}} onClick={() => setHistory(false)}>
            <Image width={16} height={16} src="/images/close_history.png" alt="close-history-icon"/>
          </div>
        </div>
      </div>
      <div className={styles.detail_body}>
        {runs.reverse().map((run) => (<div key={run.id} onClick={() => setSelectedRun(run.id)} className={styles.history_box} style={selectedRun === run.id ? {background:'#474255'} : {background:'#272335'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'10px'}}>
            <div>{run.name}</div>
            {run.notification_count > 0 && <div className={styles.notification_bubble}>{run.notification_count}</div>}
          </div>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            <div style={{display:'flex',alignItems:'center'}}>
              <div>
                <Image width={12} height={12} src="/images/call_made.png" alt="call-icon"/>
              </div>
              <div className={styles.history_info}>
                {run.calls} Calls
              </div>
            </div>
            <div style={{display:'flex',alignItems:'center',marginLeft:'7px'}}>
              <div>
                <Image width={12} height={12} src="/images/schedule.png" alt="schedule-icon"/>
              </div>
              <div className={styles.history_info}>
                {convertToMinutes(run.last_active)}m ago
              </div>
            </div>
          </div>
        </div>))}
      </div>
    </div>
  </>)
}