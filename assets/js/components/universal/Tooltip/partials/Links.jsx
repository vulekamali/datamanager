import CloseIcon from './CloseIcon.jsx';


export default function Links({ actions, closeAction }) {
  return (
    <div className="Tooltip-links">

      <span className="Tooltip-linkWrap is-close" onClick={closeAction}>
        <span className="Tooltip-closeIcon">
          <CloseIcon />
        </span>
        <span className="Tooltip-link">
          Close
        </span>
      </span>

      {
        actions.map(({ url, title }) => {
          return (
            <a className="Tooltip-linkWrap" href={url}>
              <div className="Tooltip-link">{ title }</div>
            </a>
          );
        })
      }
    </div>
  );
}
