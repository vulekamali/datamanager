import { h } from 'preact';
import CssTransitionGroup from 'preact-css-transition-group';
import Icon from './../../Icon/index.jsx';


export default function Modal({ markup, title, closeModal }) {
  const buildModal = () => {

    if (!markup || !title) {
      return null;
    }

    return (
      <div className="Modals-inner">
        <div className="Modals-overlay" onClick={closeModal} aria-hidden />
        <div className="Modals-boxWrap">
          <div className="Modals-box">
            <div className="Modals-heading">{title}</div>
            <div className="Modals-content">{markup}</div>
          </div>
          <button className="Modals-close" onClick={closeModal}>
            <Icon type="close" size="small" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="Modals">
      <CssTransitionGroup
        transitionName="is"
        transitionEnterTimeout={300}
        transitionLeaveTimeout={300}
      >
        {buildModal()}
      </CssTransitionGroup>
    </div>
  );
}
