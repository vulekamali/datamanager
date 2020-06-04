import { h, Component, render } from 'preact';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';
import updateQs from './../../../utilities/js/helpers/updateQs.js';
import { DeptSearch, makeGroups } from './index.jsx';
import filterResults from './partials/filterResults.js';
import fetchWrapper from './../../../utilities/js/helpers/fetchWrapper.js';

const originalBudgetGroups = [
  'estimates-of-provincial-revenue-and-expenditure',
  'people-s-guides',
  'occasional-budget-documents',
  'tax-pocket-guides',
  'appropriation-bills',
  'budget-highlights',
  'budget-reviews',
  'budget-speeches',
  'division-of-revenue-bills',
  'estimates-of-national-expenditure',
];
const adjustedBudgetGroups = [
  'adjusted-estimates-of-national-expenditure',
  'adjusted-estimates-of-provincial-revenue-and-expenditure',
  'division-of-revenue-amendment-bills',
  'adjustments-appropriation-bills',
  'medium-term-budget-policy-statements',
];

class DeptSearchContainer extends Component {
  constructor(props) {
    super(props);
    const filters = {
      keywords: this.props.phrase || '',
      sphere: this.props.sphere || 'all',
      province: this.props.province || 'all',
    };

    this.state = {
      loading: false,
      open: null,
      results: filterResults(filters, this.props.governments),
      filters,
      resources: {},
    };

    this.eventHandlers = {
      updateDropdown: this.updateDropdown.bind(this),
      updateKeywords: this.updateKeywords.bind(this),
    };

    this.requestResources();
  }

  componentWillUpdate(nextProps, nextState) {
    updateQs({
      ...window.vulekamali.qs,
      phrase: nextState.filters.keywords,
      sphere: nextState.filters.sphere,
      province: nextState.filters.province,
    });
  }

  updateKeywords(keywords) {
    const filters = {
      ...this.state.filters,
      keywords,
    };

    this.setState({ filters });
    this.setState({ results: filterResults(filters, this.props.governments) });
  }

  updateDropdown(filter, value) {
    if (this.state.open === filter) {
      this.setState({ open: null });
    } else {
      return this.setState({ open: filter });
    }

    const filters = {
      ...this.state.filters,
      province: 'all',
      [filter]: value,
    };

    this.setState({ filters });
    return this.setState({ results: filterResults(filters, this.props.governments) });
  }

  requestResources() {
    const url = resourcesUrl(this.props.ckanUrl, this.props.financialYear);
    fetchWrapper(url)
      .then((response) => {
        this.setState({resources: resultsToResources(response.result.results)});
      })
      .catch((errorResult) => console.warn(errorResult));
  }

  render() {
    return <DeptSearch state={this.state} eventHandlers={this.eventHandlers} />;
  }
}

function resourcesUrl(ckanUrl, financialYear) {
  const groupsClause = [...originalBudgetGroups, ...adjustedBudgetGroups]
        .map(g => `groups:"${g}"`)
        .join(' OR ');
  const fqParams = [
    'organization:"national-treasury"',
    `(${groupsClause})`,
    `vocab_financial_years:"${financialYear}"`,
  ].join('+');
  const searchParams = new URLSearchParams();
  searchParams.set('q', '');
  searchParams.set('fq', fqParams);
  searchParams.set('rows', '1000');
  return `${ckanUrl}/api/3/action/package_search?${searchParams.toString()}`
}

/**
 * @param {array} results - CKAN package_search action results field: an array of packages.

 * Returns an object keyed by government name, where the values are objects
 * with that government's budgetResources and adjustedBudgetResources as keys.
 */
function resultsToResources(results) {
  return results.reduce(datasetReducer, {});
}

function datasetReducer(governments, dataset) {
  const governmentName = datasetGovernment(dataset);
  if (!(governmentName in governments))
    governments[governmentName] = {
      "original": [],
      "adjusted": [],
    }
  const government = governments[governmentName];
  if (dataset.groups.some(group => originalBudgetGroups.includes(group.name)))
    government.original.push(...(dataset.resources));
  if (dataset.groups.some(group => adjustedBudgetGroups.includes(group.name)))
    government.adjusted.push(...(dataset.resources));
  return governments;
}

function datasetGovernment(dataset) {
  if (dataset.sphere.length > 1) {
    console.error("More than one sphere", dataset);
    return null;
  }
  if (dataset.sphere[0] === "national")
      return "South Africa";
  if (dataset.sphere[0] === "provincial") {
    if (dataset.province.length > 1)
      console.error("More than one province", dataset);
    return dataset.province[0];
  }
  return null;
}

function scripts() {
  const componentsList = document.getElementsByClassName('js-initDeptSearch');
  const ckanUrl = document.getElementsByTagName('body')[0].getAttribute('data-ckan-url');;

  for (let i = 0; i < componentsList.length; i++) {
    const component = componentsList[i];
    const nationalData = JSON.parse(decodeHtmlEntities(component.getAttribute('data-national-json'))).data;
    const rawProvincialData = JSON.parse(decodeHtmlEntities(component.getAttribute('data-provincial-json'))).data;
    const financialYear = decodeHtmlEntities(component.getAttribute('data-year'));

    const provincialData = rawProvincialData.sort((a, b) => {
      return a.name.localeCompare(b.name);
    });
    provincialData.forEach(p => {
      p.label = p.name
    });

    const governments = [
      {
        ...nationalData,
        label: 'National',
      },
      ...provincialData,
    ];

    const { sphere, province, phrase } = window.vulekamali.qs;

    render(
      <DeptSearchContainer {...{ governments, ckanUrl, financialYear, sphere, province, phrase }} />,
      component,
    );
  }
}


export default scripts();
