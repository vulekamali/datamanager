import { find } from 'lodash';
import extractSnippet from './extractSnippet.js';


const createLinkText = (sphere) => {
  if (sphere === 'national') {
    return 'Estimates of National Expenditure (ENE)';
  }

  return 'Estimates of Provincial Revenue and Expenditure (EPRE)';
};


const buildUrl = (isOfficial, buildDeptUrl, organization, name, groups) => {
  if (isOfficial) {
    return buildDeptUrl();
  }

  if (organization !== 'national-treasury' && groups.length < 1) {
    return `/datasets/contributed/${name}`;
  }

  return `/datasets/${groups[0].name}/${name}`;
};


const normaliseDepartmentItem = (item) => {
  const {
    extras,
    province,
    financial_year: financialYear,
    organization = {},
    title: rawTitle,
    name,
    groups,
  } = item;

  const getExtrasValue = (key) => {
    const obj = find(extras, extra => extra.key === key) || { value: null };
    return obj.value;
  };

  const isOfficial = organization.name === 'national-treasury' && !!getExtrasValue('department_name_slug');

  const year = financialYear[0];
  const region = getExtrasValue('geographic_region_slug');
  const regionString = region === 'south-africa' ? 'National' : province[0];
  const regionSlug = region === 'south-africa' ? 'national' : `provincial/${region}`;

  const nameSlug = getExtrasValue('department_name_slug');
  const nameString = getExtrasValue('department_name');
  const { text: snippet, url: sourceUrl } = extractSnippet(item, isOfficial) || {};

  const buildDeptName = () => `${regionString} Department: ${nameString}`;
  const title = isOfficial ? buildDeptName() : rawTitle;

  const buildDeptUrl = () => `/${year}/${regionSlug}/departments/${nameSlug}`;
  const url = buildUrl(isOfficial, buildDeptUrl, organization.name, name, groups);
  const sourceText = isOfficial ? createLinkText(regionSlug) : null;

  return {
    title,
    url,
    snippet,
    contributor: groups.length < 1 && organization.title,
    source: {
      text: sourceText,
      url: sourceUrl,
    },
  };
};


export default function normaliseServerResponse(reponseObj) {
  const { count, results } = reponseObj.result;

  return {
    count,
    items: results.map(normaliseDepartmentItem),
  };
}
