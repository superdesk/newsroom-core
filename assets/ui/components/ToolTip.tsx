import * as React from 'react';
import PropTypes from 'prop-types';
import {Tooltip} from 'bootstrap';
import {isTouchDevice} from 'assets/utils';

export class ToolTip extends React.PureComponent<any, any> {
    tooltip: any;
    elem: any;
    static propTypes: any;

    constructor(props: any) {
        super(props);

        this.tooltip = null;
    }

    getFirstChild() {
        return this.elem && this.elem.firstChild ?
            this.elem.firstChild :
            null;
    }

    componentDidMount() {
        if (!isTouchDevice()) {
            const child = this.getFirstChild();

            if (!child) {
                console.error('No child supplied to <ToolTip>!');
            } else if (!child.getAttribute('title')) {
                console.error('Child of <ToolTip> must have a "title" attribute!');
            } else {
                this.tooltip = new Tooltip(child, {
                    trigger: 'hover',
                    placement: this.props.placement || 'top'
                });
            }
        }
    }

    componentWillUnmount() {
        if (this.tooltip) {
            this.tooltip.dispose();
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
    placement: PropTypes.string,
};
