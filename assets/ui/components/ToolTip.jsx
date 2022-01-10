import * as React from 'react';
import PropTypes from 'prop-types';
import {isTouchDevice} from 'utils';

export class ToolTip extends React.PureComponent {
    getFirstChild() {
        return !isTouchDevice() && this.elem && this.elem.firstChild && this.elem.firstChild ?
            this.elem.firstChild :
            null;
    }

    componentDidMount() {
        const child = this.getFirstChild();

        if (!child) {
            console.error('No child supplied to <ToolTip>!');
        } else if (!child.getAttribute('title')) {
            console.error('Child of <ToolTip> must have a "title" attribute!');
        } else {
            $(child).tooltip({trigger: 'hover'});
        }
    }

    componentWillUnmount() {
        const child = this.getFirstChild();

        if (child) {
            $(child).tooltip('dispose'); // make sure it's gone
        }
    }

    render() {
        return (
            <div
                ref={(elem) => this.elem = elem}
                style={{display: 'contents'}}
            >
                {this.props.children}
            </div>
        );
    }
}

ToolTip.propTypes = {
    children: PropTypes.node.isRequired,
};
