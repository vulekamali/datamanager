import { h } from 'preact';
import Box from './partials/Box.jsx';


export default function Tooltip({ block, children, title, description, actions, down, open, openAction, closeAction }) {

  return (
    <span className={`Tooltip${block ? ' is-block' : ''}`}>
      <div className="Tooltip-trigger" onClick={openAction}>
        {children}
      </div>
      <div className={`Tooltip-boxWrap${open ? ' is-open' : ''}${down ? ' is-down' : ''}`}>
        <div className="Tooltip-modalCover" onClick={closeAction} />
        <Box {...{ title, description, actions, down, closeAction }} />
      </div>
    </span>
  );
}