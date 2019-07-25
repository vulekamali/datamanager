import React from 'react';
import { mockProps, Tprops } from '../schema';
import Treemap from '../index';

const passedProps: Tprops = mockProps();

const Test = () => <Treemap {...passedProps} />;

export default Test;
