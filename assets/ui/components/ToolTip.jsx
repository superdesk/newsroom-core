import * as React from 'react';
import PropTypes from 'prop-types';
import {isTouchDevice} from 'utils';

export class ToolTip extends React.PureComponent {
    componentDidMount() {
        if (!isTouchDevice()) {
            this.elem && $(this.elem).tooltip({trigger: 'hover'});
        }
    }

    componentWillUnmount() {
        this.elem && $(this.elem).tooltip('dispose'); // make sure it's gone
    }

    render() {
        return this.props.render((elem) => this.elem = elem);
    }
}

ToolTip.propTypes = {
    render: PropTypes.func.isRequired,
};
