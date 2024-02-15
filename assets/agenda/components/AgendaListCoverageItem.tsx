import React from 'react';
import classNames from 'classnames';
import {isEqual} from 'lodash';

import {IAgendaItem, ICoverage, IUser} from 'interfaces';
import {gettext} from '../../utils';
import {
    getCoverageIcon,
    getCoverageTooltip,
    isCoverageBeingUpdated,
    isCoverageForExtraDay,
    isWatched,
    WORKFLOW_COLORS,
    COVERAGE_STATUS_COLORS
} from '../utils';

interface IProps {
    group: string;
    planningItem?: IAgendaItem;
    user: IUser['_id'];
    coverage: ICoverage;
    showBorder?: boolean;
}

interface IState {
    coverageClass: string;
    beingUpdated: boolean;
    isWatched: boolean;
    watchText: string;
    isCoverageForExtraDay: boolean;
    tooltip: string;
}

class AgendaListCoverageItem extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = this.getUpdatedState();
    }

    shouldComponentUpdate(nextProps: IProps) {
        return !isEqual(this.props.coverage, nextProps.coverage);
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (!isEqual(prevProps.coverage, this.props.coverage)) {
            this.setState(this.getUpdatedState());
        }
    }

    getUpdatedState(): IState {
        const watched = isWatched(this.props.coverage, this.props.user);
        const watchText = watched ? gettext('(Watching)') : '';
        const beingUpdated = isCoverageBeingUpdated(this.props.coverage);

        return {
            coverageClass: `icon--coverage-${getCoverageIcon(this.props.coverage.coverage_type)}`,
            beingUpdated: beingUpdated,
            isWatched: watched,
            watchText: watchText,
            isCoverageForExtraDay: isCoverageForExtraDay(this.props.coverage, this.props.group),
            tooltip: `${watchText} ${getCoverageTooltip(this.props.coverage, beingUpdated)}`,
        };
    }

    render() {
        const props = this.props;
        const state = this.state;
        const coverage_icon = COVERAGE_STATUS_COLORS[props.coverage.coverage_status] ||
            WORKFLOW_COLORS[props.coverage.workflow_status];
        return (
            !props.group ||
            props.coverage.scheduled == null ||
            (
                state.isCoverageForExtraDay &&
                (
                    props.planningItem == null ||
                    props.coverage.planning_id === props.planningItem.guid
                )
            )
        ) && (
            <span
                className={classNames('wire-articles__item__icon',`${coverage_icon}`, {'dashed-border': props.showBorder})}
                title={state.tooltip}
            >
                <i className={`${state.coverageClass}`}>
                    {state.beingUpdated && <i className="blue-circle" />}
                    {state.isWatched &&
                      <i className="blue-circle blue-circle--pale blue-circle--left" />}
                </i>
            </span>
        );
    }
}

export default AgendaListCoverageItem;
