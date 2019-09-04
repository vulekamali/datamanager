import { h } from 'preact';
import DeptControl from './../DeptControl/index.jsx';
import DeptGroup from './../DeptGroup/index.jsx';


const onlyEpreView = (slug, name, epresData) => {
  return (
    <div className="DeptSearch-groupWrap">
      <DeptGroup
        empty
        map={slug}
        name={name}
        epre={epresData && (epresData[slug] || null)}
      />
    </div>
  );
};


const normalView = (slug, departments, name) => {
  return (
    <div className="DeptSearch-groupWrap">
      <DeptGroup
        map={slug}
        linksArray={departments}
        name={name}
        doubleRow={slug === 'south-africa'}
      />
    </div>
  );
};


const emptyNotification = (
  <div className="Section is-bevel is-dark">
    <div className="Section-card is-invisible">
      <div className="Section-title">
        No results found
      </div>
      <div>
        Please try changing or broadening your search term
      </div>
    </div>
  </div>
);


const showResults = (results, emptyGroups, epresData) => {
  const hasItemsInDept = ({ departments }) => departments.length > 0;

  if (results.filter(hasItemsInDept).length < 1) {
    return emptyNotification;
  }

  return results.map(
    ({ name, slug, departments }) => {
      if (emptyGroups.indexOf(slug) > -1) {
        return onlyEpreView(slug, name, epresData);
      } else if (departments.length > 0) {
        return normalView(slug, departments, name);
      }

      return null;
    },
  );
};


export default function DeptSearchMarkup({ state, eventHandlers, epresData }) {
  const { results, emptyGroups } = state;

  return (
    <div className="DeptSearch">
      <div className="DeptSearch-wrap">
        <h3 className="u-sReadOnly">Filters</h3>
        <ul className="DeptSearch-list">
          <li>
            <DeptControl
              open={state.open}

              keywords={state.filters.keywords}
              sphere={state.filters.sphere}
              province={state.filters.province}

              updateFilter={eventHandlers.updateDropdown}
              changeKeywords={eventHandlers.updateKeywords}
            />
          </li>
        </ul>
        <h3 className="u-sReadOnly">Results</h3>
        <div className="DeptSearch-results">
          {showResults(results, emptyGroups, epresData)}
        </div>
      </div>
    </div>
  );
}
