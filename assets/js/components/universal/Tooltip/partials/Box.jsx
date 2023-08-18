import React from 'react';
import Links from './Links.jsx';


export default function Box({ title, description, actions, down, closeAction }) {
  return (
    <div className="Tooltip-box">
      <div className={`Tooltip-content${down ? ' is-down' : ''}`}>
        <div className="Tooltip-contentWrap">
          <div className="Tooltip-shadowBox">
            <div className="Tooltip-infoBox">
              <div className="Tooltip-title">{title}</div>
              <div className="Tooltip-text">{description}</div>
              <Links {...{ actions, closeAction }} />
            </div>
            <div className={`Tooltip-triangle${down ? ' is-down' : ''}`} />
          </div>
        </div>
      </div>
    </div>
  );
}
