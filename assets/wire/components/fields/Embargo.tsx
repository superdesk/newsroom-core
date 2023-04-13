import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment-timezone';
import classNames from 'classnames';
import {Tooltip} from 'bootstrap';
import {getEmbargo, fullDate, gettext} from 'assets/utils';

export class Embargo extends React.Component<any, any> {
    timeout: any;
    tooltip: any;
    elem: any;
    static propTypes: any;

    constructor(props: any) {
        super(props);
        this.state = {
            embargo: getEmbargo(props.item),
            forceRender: false,
        };
        this.timeout = null;
        this.tooltip = null;
    }

    componentDidMount() {
        if (this.state.embargo) {
            if (this.elem) {
                this.tooltip = new Tooltip(this.elem, {
                    placement: 'bottom',
                    title: fullDate(this.state.embargo),
                });
            }

            // Calculate the duration for when the embargo is lifted
            const embargo = moment(this.props.item.embargoed);
            const embargoLiftsIn = moment.duration(embargo.diff(moment()));

            // Make sure we aren't setting a timeout that is too big
            if (embargoLiftsIn.asHours() < 48) {
                this.timeout = setTimeout(() => {
                    this.timeout = null;
                    this.setState({
                        embargo: getEmbargo(this.props.item),
                        forceRender: true,
                    });
                }, embargoLiftsIn.asMilliseconds());
            }
        }
    }

    componentWillUnmount() {
        if (this.elem && this.tooltip) {
            this.tooltip.dispose();
        }

        if (this.timeout != null) {
            clearTimeout(this.timeout);
        }
    }

    render() {
        if (!this.state.embargo && !this.state.forceRender) {
            return null;
        }

        return (
            <span
                ref={(elem) => this.elem = elem}
                className={classNames('label', {
                    'me-2': !this.props.isCard,
                    'label--red': !this.state.forceRender,
                    'label--available': this.state.forceRender,
                })}
            >{gettext('embargo')}</span>
        );
    }
}

Embargo.propTypes = {
    item: PropTypes.shape({
        embargoed: PropTypes.string,
    }),
    isCard: PropTypes.bool
};
