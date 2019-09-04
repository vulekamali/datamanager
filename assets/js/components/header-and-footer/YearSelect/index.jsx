import { h } from 'preact';
import queryString from 'query-string';
import Tooltip from './../../universal/Tooltip/index.jsx';

const navToYearPage = (event, page) => {
  event.preventDefault();
  window.location.href = `${page}?${queryString.stringify(window.vulekamali.qs)}`;
};


export default function YearSelectMarkup({ sticky, jsonData, updateNode, tooltip, open, updateItem, search, loading, year, newYear }) {

  const items = jsonData.map((data) => {
    const Tag = data.active || data.direct === false ? 'span' : 'a';
    const toggleOpen = () => updateItem('open', !open);

    if (!data.direct) {
      return (
        <li
          className={`YearSelect-item${ data.active ? ' is-active' : '' }`}
          onClick={ data.active ? toggleOpen : null }
        >
          <Tooltip
            block
            title="Content Unavailable"
            description={`There is no exact match for this department in ${data.name}.`}
            year={year}
            openAction={() => updateItem('tooltip', data.name)}
            closeAction={() => updateItem('tooltip', null)}
            open={data.name === tooltip}
            down
            actions={[
              {
                url: `/${data.name}/departments`,
                title: `View ${data.name} Departments`,
              },
            ]}
          >
            <Tag
              href={data.active || data.direct === false ? null : data.url}
              className="YearSelect-link u-cursorDefault"
            >
              {data.name}
            </Tag>
          </Tooltip>
        </li>
      );
    }

    const clickEvent = data.active || data.direct === false ? null : event => navToYearPage(event, data.url);

    return (
      <li
        className={`YearSelect-item${ data.active ? ' is-active' : '' }`}
        onClick={ data.active ? toggleOpen : null }
        >
        <Tag
          href={data.active || data.direct === false ? null : data.url}
          className="YearSelect-link"
          onClick={clickEvent}
        >
          {data.name}
        </Tag>
      </li>
    );
  });

  const placeholder = (
    <div className={`YearSelect-bar is-loading${open ? ' is-open' : ''}`} />
  );

  const realData = (
    <ul className={`YearSelect-bar${open ? ' is-open' : ''}`}>
      {items}
    </ul>
  );

  const instance = (
    <div className="YearSelect-instance">
      <div className="YearSelect-wrap">
        <h2 className="YearSelect-title">
          <span className="YearSelect-titleExtra">Show data for a </span>
          <span >financial year</span>
        </h2>
        <div className="YearSelect-content">
          { loading ? placeholder : realData }
        </div>
      </div>
    </div>
  );

  return (
    <div className="YearSelect">
      <div className="YearSelect-static" ref={node => updateNode(node)}>
        {instance}
      </div>
      <div aria-hidden className={`YearSelect-fixed${sticky ? ' is-active' : ''}`}>
        {instance}
      </div>
    </div>
  );
}
