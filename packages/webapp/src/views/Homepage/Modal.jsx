import React from 'react';
import styled from 'styled-components';
import Youtube from 'react-responsive-embed';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import Zoom from '@material-ui/core/Zoom';
import { PrimaryButton } from './styled';


const StyledDialogActions = styled(DialogActions)`
  && {
    margin: 8px 20px 20px;
  }
`;


const placeholderText = (
  <DialogContentText>
    A live video-stream of the budget speech will be available on the Vulekamali homepage at <strong>14:00 PM</strong> on <strong>22 February 2019</strong>.
  </DialogContentText>
);


const Modal = ({ open, closeModal, videoUrl }) => (
  <Dialog 
    {...{ open }}
    onClose={closeModal}
    TransitionComponent={Zoom}
  >
    <DialogTitle>Budget Speech 2019</DialogTitle>
    <DialogContent>
      {videoUrl ? <Youtube src={videoUrl} /> : placeholderText}
    </DialogContent>
    <StyledDialogActions>
      <PrimaryButton onClick={closeModal}>
        Close
      </PrimaryButton>
    </StyledDialogActions>
  </Dialog>
);


export default Modal;


// Modal.propTypes = {
//   closeModal: t.func.isRequired,
//   videoUrl: t.string,
// }


// Modal.defaultProps = {
//   videoUrl: null,
// }