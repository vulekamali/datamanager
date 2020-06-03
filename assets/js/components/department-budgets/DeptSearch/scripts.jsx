import { h, Component, render } from 'preact';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';
import updateQs from './../../../utilities/js/helpers/updateQs.js';
import { DeptSearch, makeGroups } from './index.jsx';
import filterResults from './partials/filterResults.js';
import fetchWrapper from './../../../utilities/js/helpers/fetchWrapper.js';

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
    console.log("governments", filterResults(filters, this.props.governments), this.props.governments);
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
    const ckanUrl = this.props.ckanUrl;
    const financialYear = this.props.financialYear;
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
    const groupsClause = [...originalBudgetGroups, ...adjustedBudgetGroups]
          .map(g => `groups:"${g}"`)
          .join(' OR ')
    const fqParams = [
      'organization:"national-treasury"',
      `(${groupsClause})`,
      `vocab_financial_years:"${financialYear}"`,
    ].join('+');
    const searchParams = new URLSearchParams();
    searchParams.set('q', '');
    searchParams.set('fq', fqParams);
    const url = `${ckanUrl}/api/3/action/package_search?${searchParams.toString()}`
    fetchWrapper(url)
      .then((response) => console.log(response))
      .catch((errorResult) => console.warn(errorResult));
  }

  render() {
    return <DeptSearch state={this.state} eventHandlers={this.eventHandlers} />;
  }
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
