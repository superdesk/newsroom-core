import React from 'react';
import moment from 'moment';
import classNames from 'classnames';

import {IAgendaItem} from 'interfaces';
import {bem} from 'ui/utils';
import {gettext} from 'utils';

interface IProps {
    item: IAgendaItem;
    borderRight?: boolean;
    alignCenter?: boolean;
}

interface IState {
    timeText: string;
}

class AgendaItemTimeUpdater extends React.Component<IProps, IState> {
    interval: number;
    timerIntervalId: number;

    constructor(props: any) {
        super(props);

        this.state = {timeText: ''};
        this.interval = 60; // In minutes
        this.timerIntervalId = 0;  // handle ID of our interval object

        this.updateState = this.updateState.bind(this);
    }

    componentDidMount() {
        this.activateTimer(this.props.item);
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (
            this.props.item._created !== prevProps.item._created ||
            this.props.item._updated !== prevProps.item._updated
        ) {
            this.activateTimer(this.props.item);
        }
    }

    componentWillUnmount() {
        this.deactivateTimer();
    }

    activateTimer(item: IAgendaItem) {
        // Deactivate if a timer already exits
        this.deactivateTimer();

        if (!item || this.isItemPastTime(item)) {
            return;
        }

        // Set current state - no need to validate time
        this.updateState(item, false);

        // timer set for minute interval
        this.timerIntervalId = window.setInterval(this.updateState, 60000, item);
    }

    deactivateTimer() {
        if (this.timerIntervalId > 0) {
            clearInterval(this.timerIntervalId);
            this.setState({timeText: ''});
        }
    }

    isItemPastTime(item: any) {
        // Check if the updated (and created) time is past the interval duration
        return item && (moment().diff(moment(item._created), 'minutes') >= this.interval &&
            moment().diff(moment(item._updated), 'minutes') >= this.interval);
    }

    updateState(item: IAgendaItem, checkPastTime = true) {
        if (checkPastTime && this.isItemPastTime(item)) {
            this.deactivateTimer();
            return;
        }

        const created = moment(item.firstcreated);
        const updated = moment(item.versioncreated);
        const createdDiff = moment().diff(created, 'minutes');
        const updatedDiff = moment().diff(updated, 'minutes');

        let itemState = gettext('Posted');
        let timeDiff = createdDiff;

        if (updated.isAfter(created, 'minutes')) {
            itemState = gettext('Updated');
            timeDiff = updatedDiff;
        }

        if (timeDiff === 0) {
            this.setState({timeText: gettext('{{ action }} just now', {action: itemState})});
        } else {
            this.setState({timeText: gettext('{{ action }} {{ minutes }} minute(s) ago', {
                action: itemState,
                minutes: timeDiff,
            })});
        }
    }

    render() {
        if (this.state.timeText.length === 0) {
            return null;
        }

        const className = classNames(
            bem(
                'wire-articles__item',
                'meta-time',
                {'border-right': this.props.borderRight === true}
            ),
            {'align-self-center': this.props.alignCenter === true}
        );

        return(
            <div className={className}>
                <div className="label label--blue">{this.state.timeText}</div>
            </div>
        );
    }
}

export default AgendaItemTimeUpdater;
