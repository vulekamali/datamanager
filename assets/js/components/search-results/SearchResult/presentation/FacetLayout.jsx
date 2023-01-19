

const buildSnippet = (snippet, tab) => {
  if (tab === 'contributed' && !snippet.organization) {
    return null;
  }
  return (
    <div>
      <div className="u-marginBottom20 u-lineHeight16" dangerouslySetInnerHTML={{ __html: snippet.text }} />
      <div>
        <span>Source:&nbsp;</span>
        <a target="_blank" href={snippet.url}>{createLinkText(tab, snippet.organization)}</a>
      </div>
    </div>
  );
};


function ItemPreview({ title, url, snippet, paddingOverride, source, contributor }) {
  const showContributor = contributor && contributor !== 'National Treasury';
  const hasSource = source.text && source.url;

  return (
    <div key={url} className={`Section u-marginBottom20 is-invisible${paddingOverride ? ' u-padding0' : ''}`}>
      <a href={url} className="Section-title" dangerouslySetInnerHTML={{ __html: title }} />
      <div className="u-marginTop15 u-marginBottom15">
        {showContributor ? `Contributor: ${contributor}` : null}
      </div>
      <div className="u-marginBottom20 u-lineHeight16" dangerouslySetInnerHTML={{ __html: snippet }} />
      {hasSource ? <div><span>Source: </span><a target="_blank" href={source.url}>{source.text}</a></div> : null}
    </div>
  );
}


function ShowMoreButton({ addPage }) {
  return (
    <div className="u-textAlignCenter">
      <button className="Button is-secondary is-inline" onClick={addPage}>
        Show more
      </button>
    </div>
  );
}


export default function FacetLayout({ count, response = {}, year, tab, tabKey, addPage, page }) {
  const { items } = response[tabKey];
  return (
    <div>
      <div>
        <div className="Section is-invisible">
          <div className="Section-title">
            <span className="u-fontWeightNormal">All {count} results found in&nbsp;</span>
            <span>{tab} for {year}</span>
          </div>
        </div>
        {items.map(({ title, url, snippet, source, contributor }) => <ItemPreview tab={tabKey} {...{ title, url, snippet, source, contributor }} />)}
      </div>
      <div>
        {count > page * 5 ? ShowMoreButton({ addPage }) : null}
      </div>
    </div>
  );
}
