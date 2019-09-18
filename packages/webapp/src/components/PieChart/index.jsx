import React from 'react';

import Media from 'react-media';

import {
  StyledCircle,
  StyledSvg,
} from './styled';

const Slice = ({amount}) => {
  return (
    <Media query="(max-width: 899px)">
      {matches =>
        matches ? (
          <StyledCircle
            r={20 / 4}
            cy={20 / 2}
            cx={20 / 2}
            strokeWidth={20 / 2 - 1}
            fill="none"
            strokeDasharray={`${((amount / 100) * Math.round(Math.PI * (20 / 2)))}, ${Math.round(Math.PI * (20 / 2))}`}
            strokeDashoffset="0"
            transform="rotate(-90 10 10)"
          />
        ) : (
          <StyledCircle
            r={40 / 4}
            cy={40 / 2}
            cx={40 / 2}
            strokeWidth={40 / 2 - 1}
            fill="none"
            strokeDasharray={`${((amount / 100) * Math.round(Math.PI * (40 / 2)))}, ${Math.round(Math.PI * (40 / 2))}`}
            strokeDashoffset="0"
            transform="rotate(-90 20 20)"
          />
        )
      }
    </Media>
  );
};

const PieChart = ({ values }) => {

  const startRanges = values.reduce(
    (result, val, i) => {
      return [
        ...result,
        val + result[i],
      ]
    },
    [0]
  );

  const slices = values.map((value, i) => {
    return <Slice start={startRanges} amount={value} key={i} />
  });

  return (
    <Media query="(max-width: 899px)">
      {matches =>
        matches ? (
          <StyledSvg
            viewBox={`0 0 20 20`}
            xmlns='http://www.w3.org/2000/svg'
          >
            {slices}
          </StyledSvg>
        ) : (
          <StyledSvg
            viewBox={`0 0 40 40`}
            xmlns='http://www.w3.org/2000/svg'
          >
            {slices}
          </StyledSvg>
        )
      }
    </Media>
  )
};

export default PieChart;
