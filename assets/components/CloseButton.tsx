import React from 'react';
import {gettext} from 'utils';
import {IconButton} from './IconButton';

interface IProps {
    onClick: (event: React.MouseEvent) => void;
    disabled?: boolean;
}

class CloseButton extends React.Component<IProps> {
    render() {
        return (
            <IconButton
                icon='close-thin'
                id='hide-sidebar'
                data-bs-dismiss='modal'
                ariaLabel={gettext('Close')}
                ariaHidden={true}
                disabled={this.props.disabled}
                onClick={this.props.onClick}
            />
        );
    }
}

export default CloseButton;
