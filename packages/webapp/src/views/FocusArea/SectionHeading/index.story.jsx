import React from 'react';
import { storiesOf } from '@storybook/react';

import SectionHeading from './index';

const share = () => <SectionHeading title='Provincial Budget Summary' share>Children Components</SectionHeading>;
const noShare = () => <SectionHeading title='Provincial Budget Summary'>Children Components</SectionHeading>;
const shareString = () => <SectionHeading title='Provincial Budget Summary' share='addTextHere'>Children Components</SectionHeading>;


storiesOf('components.SectionHeading', module)
  .add('Share', share)
  .add('No Share', noShare)
  .add('Share is a String', shareString)
