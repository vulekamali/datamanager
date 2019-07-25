import styled from 'styled-components';

import { Select } from '@material-ui/core';

const CustomizedForm = styled.div`
  width: 100%;
  margin-top: 16px;
  margin-bottom: 16px;

  @media screen and (min-width: 600px) {
    margin-top: 24px;
    margin-bottom: 0;
  }
`;


const SelectPreview = styled(Select)`
  background: #fff;

  && {
    width: 100%;

    @media screen and (min-width: 600px) {
      max-width: 616px;
    }

    & .icon {
      color: #000;
      background-color: #d7d7d7;
      height: 100%;
      top: 0;
      width: 42px;
      padding: 0 10px;

      @media screen and (min-width: 600px) {
        width: 64px;
        padding: 0 20px;
      }
    }

    & .selectMenu {
      padding-left: 16px;
      padding-right: 50px;
      height: 42px;
      box-sizing: border-box;
      width: 100%;
      font-size: 14px;
      font-weight: 900;
      background: #fff;
      line-height: 30px;
      letter-spacing: 0.15px;
      color: #000;
      border: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;

      @media screen and (min-width: 600px) {
        height: 64px;
        font-size: 24px;
        line-height: 49px;
        padding-right: 80px;
      }
    }
  }
`;


export {
  CustomizedForm,
  SelectPreview
}

export default {
  CustomizedForm,
  SelectPreview
}