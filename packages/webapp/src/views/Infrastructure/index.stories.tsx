import React, { createElement, Component } from 'react';
import { storiesOf } from '@storybook/react';
import Infrastructure from './index';

import {
  Link
} from 'react-router-dom'

const currentProps = {
  "dataset_url": "/datasets/infrastructure-projects/major-infrastructure-projects-by-national-departments",
  "description": "Infrastructure projects in South Africa for 2019-20",
  "projects": [
      {
          "coordinates": [
              {
                  "latitude": -33.517731,
                  "longitude": 21.599253
              }
          ],
          "dataset_url": "/datasets/infrastructure-projects/major-infrastructure-projects-by-national-departments",
          "department": {
              "budget_document": "https://data.vulekamali.gov.za/dataset/97ac7669-f7a4-40b6-a5bf-7843666fe0b5/resource/10d89fd3-0c5e-44b4-8b90-bb328c73586f/download/vote-36-water-and-sanitation.pdf",
              "name": "Water and Sanitation",
              "url": "/2019-20/national/departments/water-and-sanitation"
          },
          "description": "Upgrading of wastewater treatment works",
          "detail": "/infrastructure-projects/water-and-sanitation-calitzdorp-and-ladismith-w",
          "expenditure": [
              {
                  "amount": 0,
                  "budget_phase": "Audited Outcome",
                  "year": 2015
              },
              {
                  "amount": 0,
                  "budget_phase": "Audited Outcome",
                  "year": 2016
              },
              {
                  "amount": 0,
                  "budget_phase": "Audited Outcome",
                  "year": 2017
              },
              {
                  "amount": 0,
                  "budget_phase": "Adjusted Appropriation",
                  "year": 2018
              },
              {
                  "amount": 15000000,
                  "budget_phase": "MTEF",
                  "year": 2019
              },
              {
                  "amount": 30000000,
                  "budget_phase": "MTEF",
                  "year": 2020
              },
              {
                  "amount": 30000000,
                  "budget_phase": "MTEF",
                  "year": 2021
              }
          ],
          "infrastructure_type": "Waste Water Services",
          "name": "Calitzdorp and Ladismith W",
          "nature_of_investment": "Upgrading and additions",
          "page_title": "Calitzdorp and Ladismith W - vulekamali",
          "projected_budget": 75000000.0,
          "provinces": [
              "Western Cape"
          ],
          "slug": "/infrastructure-projects/water-and-sanitation-calitzdorp-and-ladismith-w",
          "stage": "Feasibility",
          "total_budget": 77459000
      }
  ],
  "selected_tab": "infrastructure-projects",
  "slug": "infrastructure-projects",
  "title": "Infrastructure Projects - vulekamali"
}


const isConnectionYear = year => year === '2017' || year === '2018';


const buildEne = url => ({
  heading: 'Read more in the Department Budget',
  format: 'PDF',
  link: url,
});


const datasetUrl = url => ({
  heading: 'Infrastructure Project Data',
  format: 'CSV',
  link: url,
});

const parseProjects = (projects, dataset_url) => projects.map(project => ({
  id: project.slug,
  subheading: project.department.name,
  heading: project.name,
  points: project.coordinates.map(({ latitude: y, longitude: x }, id) => ({ id: id.toString(), x, y })),
  activeProvinces: project.provinces,
  stage: project.stage,
  totalBudget: project.total_budget,
  projectedBudget: project.projected_budget,
  description: project.description,
  link: project.slug,
  resources: [
    buildEne(project.department.budget_document),
    datasetUrl(dataset_url),
  ].filter(({ link }) => !!link),
  chartData: project.expenditure.map(obj => ({
    name: obj.year,
    Actual: obj.budget_phase === 'Audited Outcome' ? obj.amount : null,
    Projected: obj.budget_phase !== 'Audited Outcome' ? obj.amount : null,
    Connection : isConnectionYear(obj.year) ? obj.amount : null,
  })),
  sideInfo: {
    investment: project.nature_of_investment,
    infrastructure: project.infrastructure_type,
    department: project.department,
  },
}))


const projects = parseProjects(currentProps.projects, currentProps.dataset_url);
const points = [];
const budgetReviewUrl = null;
const projectId = "water-and-sanitation-calitzdorp-and-ladismith-w";
const details = true;

const props = {
  projects,
  points,
  budgetReviewUrl,
  projectId,
  details
}
const bob = () => <Infrastructure { ...props } />;

storiesOf('views.Infrastructure', module)
  .add('Details bob', bob);
