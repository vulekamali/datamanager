import React, { Fragment } from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import LeftIcon from '@material-ui/icons/KeyboardArrowLeft';
import RightIcon from '@material-ui/icons/KeyboardArrowRight';
import { darken } from 'polished';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

import trimValues from '../../helpers/trimValues';

const xAxisStyles = {
  fontSize: '12px',
  fontFamily: 'Lato',
  fontWeight: 700,
  fill: 'black',
};

const yAxisStyles = {
  fontSize: '12px',
  fontFamily: 'Lato',
  fontWeight: 700,
  fill: 'black',
};

const axisTrimValue = value => `R${trimValues(value, true)}`;

const StyledTooltip = styled(Paper)`
  && {
    background: #76b649;
    border-radius: 5px;
    color: white;
    font-size: 16px;
    font-family: Lato;
    padding: 10px;
  }
`;

const Content = ({ payload = [] }) => {
  const filtered = payload.filter(({ name }) => name !== 'Connection');

  const { name, value } = filtered[0] || {};

  return (
    <Fragment>
      <StyledTooltip>
        {name}: R{trimValues(value, true)}
      </StyledTooltip>
    </Fragment>
  );
};

const Dot = ({ cx, cy }) => {
  if (!cx || !cy) {
    return null;
  }

  const isMobile = window.innerWidth < 500;

  return <circle {...{ cx, cy }} fill={isMobile ? 'none' : '#76B649'} stroke="none" r="4" />;
};

const ActiveDot = ({ cx, cy }) => {
  if (!cx || !cy) {
    return null;
  }

  return <circle {...{ cx, cy }} fill="#76B649" stroke="none" r="7" />;
};

const GreyButton = styled(Button)`
  &&& {
    background: black;
    border-radius: 50px;
    min-width: 36px;
    width: 36px;
    height: 36px;
    text-transform: none;
    font-family: Lato;
    font-size: 16px;
    font-weight: 700;
    box-shadow: none;
    opacity: ${({ disabled }) => (disabled ? 0.2 : 1)};
    margin-right: 4px;
    margin-left: 4px;
    fill: white;
    color: white;

    &:hover {
      background: ${darken(0.1, '#C4C4C4')};
    }
  }
`;

const InfraChart = ({ data }) => {
  const renderActual = data
    .map(item => {
      return item.Actual !== null;
    })
    .reduce((a, b) => a || b);
  const renderConnection = data
    .map(item => {
      return item.Connection !== null;
    })
    .reduce((a, b) => a || b);
  const renderProjected = data
    .map(item => {
      return item.Projected !== null;
    })
    .reduce((a, b) => a || b);

  return (
    <Fragment>
      {/* {buttons} */}
      <ResponsiveContainer width="100%" height={340}>
        <LineChart
          width={500}
          height={300}
          data={data}
          margin={{
            top: 30,
            right: 60,
            left: 30,
            bottom: 30,
          }}
        >
          <CartesianGrid stroke="#E6E6E6" />
          <XAxis
            dataKey="name"
            tickLine={false}
            dy={15}
            style={xAxisStyles}
            axisLine={{
              stroke: 'black',
              strokeWidth: 1,
            }}
          />
          <YAxis
            tickFormatter={axisTrimValue}
            dx={-15}
            style={yAxisStyles}
            tickLine={false}
            axisLine={{
              stroke: 'black',
              strokeWidth: 1,
            }}
          />
          {renderActual && (
            <Line
              dataKey="Actual"
              stroke="#76B649"
              strokeWidth={3}
              dot={<Dot />}
              activeDot={<ActiveDot />}
              isAnimationActive={false}
            />
          )}
          {renderConnection && (
            <Line
              dataKey="Connection"
              stroke="#76B649"
              strokeWidth={3}
              strokeDasharray="3 4"
              dot={false}
              activeDot={false}
              isAnimationActive={false}
            />
          )}
          {renderProjected && (
            <Line
              dataKey="Projected"
              stroke="#76B649"
              strokeWidth={3}
              strokeDasharray="3 4"
              dot={<Dot />}
              activeDot={<ActiveDot />}
              isAnimationActive={false}
            />
          )}
          <Tooltip
            active={false}
            content={<Content />}
            isAnimationActive={false}
            cursor={{
              stroke: 'black',
            }}
          />
          {/* <ReferenceLine x="'19" stroke="black" label={<Selected />} /> */}
        </LineChart>
      </ResponsiveContainer>
    </Fragment>
  );
};

export default InfraChart;
