import React from "react";
import PublicEntityControl from "./../PublicEntityControl/index.jsx";
import PublicEntityGroup from "./../PublicEntityGroup/index.jsx";

const makeGroup = (public_entities) => {
  return (
    <div className="PublicEntitySearch-groupWrap">
      <PublicEntityGroup linksArray={public_entities} />
    </div>
  );
};

const emptyNotification = (
  <div className="Section is-bevel is-dark">
    <div className="Section-card is-invisible">
      <div className="Section-title">No results found</div>
      <div>Please try changing or broadening your search terms</div>
    </div>
  </div>
);

const makeGroups = (public_entities) => {
  if (public_entities.length < 1) {
    return emptyNotification;
  }

  return makeGroup(public_entities);
};

function PublicEntitySearch({ state, eventHandlers }) {
  return (
    <div className="PublicEntitySearch">
      <div className="PublicEntitySearch-wrap">
        <h3 className="u-sReadOnly">Filters</h3>
        <ul className="PublicEntitySearch-list">
          <li>
            <PublicEntityControl
              open={state.open}
              keywords={state.filters.keywords}
              updateFilter={eventHandlers.updateDropdown}
              changeKeywords={eventHandlers.updateKeywords}
              functiongroup1={state.filters.functiongroup1}
              department={state.filters.department}
            />
          </li>
        </ul>
        <h3 className="u-sReadOnly">Results</h3>
        <div className="PublicEntitySearch-results">
          {makeGroups(state.results)}
        </div>
      </div>
    </div>
  );
}

export { PublicEntitySearch, makeGroups };
