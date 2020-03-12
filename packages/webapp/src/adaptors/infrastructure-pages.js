import axios from 'axios';
import React, { createElement, Component } from 'react';
import { render } from 'react-dom';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Infrastructure from '../views/Infrastructure';
import Loading from '../views/Loading';

const buildEne = url => ({
  heading: 'Read more in the Department Budget',
  format: 'PDF',
  link: url,
});

const datasetUrl = url => ({
  heading: 'Infrastructure Project Data',
  format: 'CSV and XLSX',
  link: url,
});

const replaceWhitespace = value => {
    if (value != null) {
        return value.replace(/\s/g,'')
    }
    return ""
};

const buildChartData = expenditure => {
  let left;
  let right;
  let needRender = true;
  let data = expenditure
    .sort((a, b) => a.year > b.year)
    .map(obj => {
      const { amount, year } = obj;
      const actual = obj.budget_phase === 'Audited Outcome' ? amount : null;
      const projected = obj.budget_phase !== 'Audited Outcome' ? amount : null;
      if (actual != null) {
        left = year;
      }
      if (projected != null && !right) {
        right = year;
      }
      if (amount === null) {
        needRender = false;
      }
      return {
        name: year,
        amount,
        Actual: actual,
        Projected: projected,
        Connection: null,
      };
    });
  if (!data.length) {
    needRender = false;
  }
  if (left && right) {
    data = data.map(obj => {
      const o = { ...obj };
      if (obj.name === left || obj.name === right) {
        return { ...o, Connection: o.amount };
      }
      return o;
    });
  }
  return { data, needRender };
};

const parseProjects = (projects, dataset_url) =>
  projects.map(project => ({
    id: project.slug,
    subheading: project.government_institution.name,
    administrationType: project.administration_type,
    heading: project.name,
    points: project.coordinates.map(({ latitude: y, longitude: x }, id) => ({
      id: id.toString(),
      x,
      y,
    })),
    activeProvinces: project.provinces,
    stage: project.stage,
    totalBudget: project.total_budget,
    projectedBudget: project.projected_budget,
    description: project.description,
    link: project.slug,
    resources: [
      buildEne(project.government_institution.budget_document),
      datasetUrl(dataset_url),
    ].filter(({ link }) => !!link),
    chartData: buildChartData(project.expenditure),
    sideInfo: {
      investment: project.nature_of_investment,
      infrastructure: project.infrastructure_type,
      department: project.government_institution,
      administrationType: project.administration_type,
      partnershipType: project.partnership_type,
      financingStructure: project.financing_structure,
      formOfPayment: project.form_of_payment,
    },

    dateOfClose: project.date_of_close,
    duration: project.duration,

    projectValueRandMillion: replaceWhitespace(project.project_value_rand_million),
  }));

class InfrastructurePages extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,
      projects: [],
      datasetUrl: null,
      points: [],
    };
  }

  componentDidMount() {
    const { projectId } = this.props;
    const apiUrl = projectId
      ? `/json/infrastructure-projects/${projectId}.json`
      : '/json/infrastructure-projects.json';

    axios.get(apiUrl).then(({ data }) => {
      this.setState({
        loading: false,
        datasetUrl: data.dataset_url,
        projects: parseProjects(data.projects, data.dataset_url),
      });
    });
  }

  render() {
    const { projects, points, loading, datasetUrl } = this.state;
    const { budgetReviewUrl, details, projectId } = this.props;

    if (loading) {
      return createElement(Loading);
    }

    return createElement(Infrastructure, {
      projects,
      points,
      datasetUrl,
      budgetReviewUrl,
      Link,
      details,
      projectId,
    });
  }
}

const node = document.querySelector('[data-webapp="infrastructure-pages"]');
const budgetReviewUrl = !!node && node.getAttribute('data-webapp-budgetReviewUrl');

const connection = () => {
  if (node) {
    return render(
      <Router>
        <div>
          <Route
            exact
            path="/infrastructure-projects"
            component={() => <InfrastructurePages {...{ budgetReviewUrl }} />}
          />
          <Route
            path="/infrastructure-projects/:projectId"
            component={({ match }) => (
              <InfrastructurePages
                {...{ budgetReviewUrl }}
                projectId={match.params.projectId}
                details
              />
            )}
          />
        </div>
      </Router>,
      node,
    );
  }
};

export default connection();
