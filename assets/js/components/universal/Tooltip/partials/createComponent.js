
import closeIcon from './closeIcon.js';

function trunc(string, length) {
    return (string.length > length) ? string.substr(0, length-1) + '&hellip;' : string;
}

export default function createComponent(title, description, content) {
  return `<span class="Tooltip js-hook">
    <div class="Tooltip-trigger js-trigger">
      ${content}
    </div>
    <div class="Tooltip-boxWrap js-box">
      <div class="Tooltip-modalCover js-modalCover"></div>
      <div class="Tooltip-box">
        <div class="Tooltip-content">
          <div class="Tooltip-contentWrap">
            <div class="Tooltip-shadowBox">
              <div class="Tooltip-infoBox">
                <div class="Tooltip-title">${title}</div>
                <div class="Tooltip-text">${ trunc(description, 200) }</div>
              </div>
              <div class="Tooltip-links">
                <span class="Tooltip-linkWrap is-close js-closeTrigger">
                  <span class="Tooltip-closeIcon">
                    ${closeIcon}
                  </span>
                  <span class="Tooltip-link">
                    Close
                  </span>
                </span>

                <a class="Tooltip-linkWrap" href="/glossary">
                  <div class="Tooltip-link">View in glossary</div>
                </a>
              </div>
              <div class="Tooltip-triangle"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </span>`;
}
