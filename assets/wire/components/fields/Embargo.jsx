import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment-timezone';
import classNames from 'classnames';

import {gettext, fullDate, getEmbargo} from 'utils';

export class Embargo extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            embargo: getEmbargo(props.item),
            forceRender: false,
        };
    }

    componentDidMount() {
        if (this.state.embargo) {
            if (this.elem) {
                $(this.elem).tooltip({
                    placement: 'bottom',
                    title: fullDate(this.state.embargo),
                });
            }

            // Calculate the duration for when the embargo is lifted
            const embargo = moment(this.props.item.embargoed);
            const embargoLiftsIn = moment.duration(embargo.diff(moment()));

            // Make sure we aren't setting a timeout that is too big
            if (embargoLiftsIn.asHours() < 48) {
                setTimeout(() => {
                    this.setState({
                        embargo: getEmbargo(this.props.item),
                        forceRender: true,
                    });
                }, embargoLiftsIn.asMilliseconds());
            }
        }
    }

    componentWillUnmount() {
        if (this.elem) {
            $(this.elem).tooltip('dispose');
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
                    'ml-4': !this.props.isCard,
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
