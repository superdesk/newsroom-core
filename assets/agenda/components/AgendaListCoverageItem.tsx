import React from 'react';
import classNames from 'classnames';
import {get, isEqual} from 'lodash';

import {gettext} from '../../utils';
import {
    getCoverageIcon,
    getCoverageTooltip,
    isCoverageBeingUpdated,
    isCoverageForExtraDay,
    isWatched,
    WORKFLOW_COLORS,
} from '../utils';

interface IProps {
    planningItem: any;
    user: string;
    coverage: any;
    showBorder: boolean;
    group: string;
}

class AgendaListCoverageItem extends React.Component<IProps, any> {
    constructor(props: IProps) {
        super(props);

        this.state = this.getUpdatedState(props);
    }

    shouldComponentUpdate(nextProps: IProps) {
        return !isEqual(this.props.coverage, nextProps.coverage);
    }

    componentWillReceiveProps(nextProps: IProps) {
        if (!isEqual(this.props.coverage, nextProps.coverage)) {
            this.setState(this.getUpdatedState(nextProps));
        }
    }

    getUpdatedState(props: IProps) {
        const watched = isWatched(props.coverage, props.user);

        const state: any = {
            coverageClass: `icon--coverage-${getCoverageIcon(props.coverage.coverage_type)}`,
            beingUpdated: isCoverageBeingUpdated(props.coverage),
            isWatched: watched,
            watchText: watched ? gettext('(Watching)') : '',
            isCoverageForExtraDay: isCoverageForExtraDay(props.coverage, props.group),
        };

        state.tooltip = `${state.watchText} ${getCoverageTooltip(props.coverage, state.beingUpdated)}`;

        return state;
    }

    render() {
        const props = this.props;
        const state = this.state;

        return (
            !props.group ||
            props.coverage.scheduled == null ||
            (state.isCoverageForExtraDay && props.coverage.planning_id === get(props, 'planningItem.guid'))
        ) && (
            <span
                className={classNames('wire-articles__item__icon', WORKFLOW_COLORS[props.coverage.workflow_status], {'dashed-border': props.showBorder})}
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
