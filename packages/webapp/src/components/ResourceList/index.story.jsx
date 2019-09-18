import React from 'react';
import { storiesOf } from '@storybook/react';
import ResourceList from './index';

const resources = [
  {
    heading: '2019 Budget Speech Documentation',
    size: null,
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 2 A',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 3 A',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 4 A',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 1',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 2 B',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 3 B',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 4 B',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 1 C',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 2 C',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 3 C',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 4 C',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 1 D',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 2 D',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 3 D',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  },
  {
    heading: 'Example 4 D',
    size: '3.3MB',
    format: 'PDF',
    link:'#',
  }
]

const basic = () => <ResourceList {...{ resources }} cite />;


storiesOf('components.ResourceList', module)
  .add('Default', basic)
