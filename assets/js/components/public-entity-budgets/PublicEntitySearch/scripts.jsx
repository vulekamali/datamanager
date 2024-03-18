import React from "react";
import ReactDOM from "react-dom";
import decodeHtmlEntities from "./../../../utilities/js/helpers/decodeHtmlEntities.js";
import updateQs from "./../../../utilities/js/helpers/updateQs.js";
import { PublicEntitySearch } from "./index.jsx";
import filterResults from "./partials/filterResults.js";

class PublicEntitySearchContainer extends React.Component {
  constructor(props) {
    super(props);
    const filters = {
      keywords: this.props.phrase || "",
      functiongroup1: this.props.functiongroup1 || "all",
      department: this.props.department || "all",
    };

    this.state = {
      loading: false,
      open: null,
      results: filterResults(
        filters,
        Object.keys(this.props.publicEntities[0]).map(
          (key) => this.props.publicEntities[0][key]
        )
      ),
      filters,
    };

    this.eventHandlers = {
      updateDropdown: this.updateDropdown.bind(this),
      updateKeywords: this.updateKeywords.bind(this),
    };
  }

  componentWillUpdate(nextProps, nextState) {
    updateQs({
      ...window.vulekamali.qs,
      phrase: nextState.filters.keywords,
      functiongroup1: nextState.filters.functiongroup1,
      department: nextState.filters.department,
    });
  }

  updateKeywords(keywords) {
    const filters = {
      ...this.state.filters,
      keywords,
    };

    this.setState({ filters });
    this.setState({
      results: filterResults(
        filters,
        Object.keys(this.props.publicEntities[0]).map(
          (key) => this.props.publicEntities[0][key]
        )
      ),
    });
  }

  updateDropdown(filter, value) {
    if (this.state.open === filter) {
      this.setState({ open: null });
    } else {
      return this.setState({ open: filter });
    }

    const filters = {
      ...this.state.filters,
      [filter]: value,
    };

    this.setState({ filters });
    return this.setState({
      results: filterResults(
        filters,
        Object.keys(this.props.publicEntities[0]).map(
          (key) => this.props.publicEntities[0][key]
        )
      ),
    });
  }

  render() {
    return (
      <PublicEntitySearch
        state={this.state}
        eventHandlers={this.eventHandlers}
      />
    );
  }
}

function scripts() {
  const componentsList = document.getElementsByClassName(
    "js-initPublicEntitySearch"
  );
  const ckanUrl = document
    .getElementsByTagName("body")[0]
    .getAttribute("data-ckan-url");

  for (let i = 0; i < componentsList.length; i++) {
    const component = componentsList[i];
    const publicEntitiesData = JSON.parse(
      decodeHtmlEntities(component.getAttribute("data-public-entities-json"))
    ).data;
    const financialYear = decodeHtmlEntities(
      component.getAttribute("data-year")
    );

    const publicEntities = [
      {
        ...publicEntitiesData,
      },
    ];

    const { department, functiongroup1, phrase } = window.vulekamali.qs;

    ReactDOM.render(
      <PublicEntitySearchContainer
        {...{
          publicEntities,
          ckanUrl,
          financialYear,
          department,
          functiongroup1,
          phrase,
        }}
      />,
      component
    );
  }
}

export default scripts();
