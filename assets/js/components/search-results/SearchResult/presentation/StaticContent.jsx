import { compact } from 'lodash';


const calcSize = (total) => {
  switch (total) {
    case 0: return null;
    case 1: return 'is-1of1';
    case 2: return 'is-1of2';
    default: return 'is-1of3';
  }
};


const calcTruncate = (total) => {
  switch (total) {
    case 0: return null;
    case 1: return 400;
    case 2: return 300;
    default: return 200;
  }
};


const buildButton = (url, count) => {
  if (url && count > 1) {
    return (
      <a className="u-marginTop20 Button is-secondary is-inline" href={url}>
        <span>View all results</span>
        <span className="u-fontWeightNormal">&nbsp;({count} Results)</span>
      </a>
    );
  }

  return null;
};


const buildGlossary = ({ title, url, count, description }, total) => {
  const truncatedDescription = description.substring(0, calcTruncate(total));
  const itemCss = [
    'Grid-item',
    calcSize(total),
  ].join(' ');

  return (
    <div className={itemCss}>
      <div className="Section is-invisible u-textAlignCenter">
        <div className="Section-title" dangerouslySetInnerHTML={{ __html: title }} />
        <div className="u-fontStyleItalic u-lineHeight16" dangerouslySetInnerHTML={{ __html: `“${truncatedDescription}”` }} />
        {buildButton(url, count)}
      </div>
    </div>
  );
};


const buildVideo = ({ title, url, count, id }, total) => {
  const itemCss = [
    'Grid-item',
    calcSize(total),
  ].join(' ');

  return (
    <div className={itemCss}>
      <div className="Section is-invisible u-textAlignCenter">
        <div className="Section-title" dangerouslySetInnerHTML={{ __html: title }} />
        <a className="SearchResult-thumbnailWrap" href={url}>
          <div className="SearchResult-iconWrap">
            <svg version="1.2" className="SearchResult-icon" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
              <path d="M85.9 48L16.9.4c-.7-.5-1.7-.6-2.5-.1-.8.4-1.3 1.2-1.3 2.1v95.2c0 .9.5 1.7 1.3 2.1.3.2.7.3 1.1.3a2 2 0 0 0 1.3-.4l69-47.6c.7-.4 1-1.2 1-2 .1-.8-.3-1.5-.9-2zm0 0" />
            </svg>
          </div>
          <img className="SearchResult-thumbnail" src={`https://img.youtube.com/vi/${id.id}/mqdefault.jpg`} alt="" />
        </a>
        <div>
          {buildButton(url, count)}
        </div>
      </div>
    </div>
  );
};

export default function StaticContent({ videos, glossary }) {
  const total = compact([videos, glossary]).length;

  if (total < 1) {
    return null;
  }

  return (
    <div className="Grid has-standardTrigger">
      <div className="Grid-inner">
        {glossary ? buildGlossary(glossary, total) : null}
        {videos ? buildVideo(videos, total) : null}
      </div>
    </div>
  );
}
