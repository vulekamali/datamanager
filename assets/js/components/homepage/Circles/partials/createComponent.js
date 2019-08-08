
import closeIcon from './closeIcon.js';

export default function createComponent(title, description, button) {
  return `<div class="Tooltip-boxWrap js-alert">
    <div class="Tooltip-modalCover js-modalCover"></div>
    <div class="Tooltip-box">
      <div class="Tooltip-content">
        <div class="Tooltip-shadowBox">
          <div class="Tooltip-title">${title}</div>
          <div class="Tooltip-text">${description}</div>
          <span class="Tooltip-linkWrap is-close js-closeTrigger">
            <span>${closeIcon}</span>
            <span class="Tooltip-link">Close</span>
          </span>
          <span class="Tooltip-linkWrap is-close js-closeTrigger">
            <span>${closeIcon}</span>
            <span class="Tooltip-link">Close</span>
          </span>
          <div class="Tooltip-triangleWrap">
            <div class="Tooltip-triangle"></div>
          </div>
        </div>
      </div>
    </div>
  </div>`;
}
