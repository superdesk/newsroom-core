import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {getConfig, gettext} from 'utils';
import {
    getCoverageStatusText,
    WORKFLOW_STATUS,
    isCoverageBeingUpdated,
    isWatched,
} from '../utils';

import AgendaInternalNote from './AgendaInternalNote';
import AgendaEdNote from './AgendaEdNote';
import ActionButton from 'components/ActionButton';

import {Tooltip} from 'bootstrap';

function getDeliveryHref(coverage: any) {
    return get(coverage, 'delivery_href');
}

function getDeliveryId(coverage: any) {
    return get(coverage, 'delivery_id');
}

export default class CoverageItemStatus extends React.Component<any, any> {
    static propTypes: any;
    static defaultProps: any;
    tooltip: any;
    elem: any;
    constructor(props: any) {
        super(props);
        this.state = {wireItem: null};
        this.filterActions = this.filterActions.bind(this);
        this.onAnchorClick = this.onAnchorClick.bind(this);
        this.tooltip = null;
    }

    onAnchorClick(e: any) {
        e.stopPropagation();
    }

    componentDidMount() {
        this.setWireItem(this.props);

        if (this.elem != null) {
            this.tooltip = new Tooltip(this.elem, {trigger: 'hover'});
        }
    }

    componentWillUnmount() {
        if (this.elem && this.tooltip) {
            this.tooltip.dispose();
        }
    }

    componentWillReceiveProps(nextProps: any) {
        this.setWireItem(nextProps);
    }

    setWireItem(props: any) {
        const wireId = getDeliveryId(props.coverage);
        if (wireId && get(props, 'wireItems.length', 0) > 0) {
            this.setState({wireItem: props.wireItems.find((w: any) => w._id === wireId)});
        }
    }

    getItemText() {
        if (this.state.wireItem) {
            return this.state.wireItem.description_text ||
                this.state.wireItem.headline ||
                this.state.wireItem.slugline;
        }

        return '';
    }

    getCoverageActions(coverage: any) {
        const actionsToShow = this.filterActions();
        const parentWatched = isWatched(this.props.item, this.props.user);
        const actions = actionsToShow.map((action: any) =>
            <ActionButton
                key={action.name}
                item={coverage}
                className='icon-button icon-button--small icon-button--bordered icon-button--tertiary'
                action={action}
                plan={this.props.item}
                isVisited={parentWatched}
                disabled={parentWatched}
            />
        );

        const content = [actions];

        if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED
            && ['video', 'video_explainer', 'picture', 'graphic'].includes(coverage.coverage_type)
            && getDeliveryHref(coverage)
        ) {
            content.unshift(
                <a
                    key="contentLink"
                    className="nh-button nh-button--small nh-button--tertiary"
                    ref={(elem) => this.elem = elem}
                    title={gettext('Open in new tab')}
                    href={coverage.delivery_href}
                    target="_blank"
                    onClick={this.onAnchorClick}
                >
                    {gettext('View Content')}
                </a>
            );
        }

        if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED
            && this.state.wireItem
            && !(this.props.hideViewContentItems || []).includes(this.state.wireItem._id)
        ) {
            content.unshift(
                this.state.wireItem._access
                    ? <a
                        key="contentLink"
                        className='nh-button nh-button--small nh-button--tertiary'
                        ref={(elem) => this.elem = elem}
                        title={gettext('Open in new tab')}
                        href={'/wire?item='+ get(coverage, 'delivery_id')}
                        target={this.props.contentLinkTarget}
                        onClick={this.onAnchorClick}
                    >
                        {gettext('View Content')}
                    </a>
                    : <a
                        key="contentLink"
                        className='nh-button nh-button--small nh-button--tertiary nh-button--disabled'
                        ref={(elem) => this.elem = elem}
                        href={`mailto:${getConfig('view_content_tooltip_email')}`}
                        target='_blank'
                        title={gettext('You don’t have access to this content, please contact help-{{email}}', {email: getConfig('view_content_tooltip_email')})}
                    >
                        {gettext('View Content')}
                    </a>
            );
        }

        return content;
    }

    filterActions() {
        return this.props.actions.filter((action: any) => !action.when ||
            action.when(this.props.coverage, this.props.user, this.props.item));
    }

    getWorkflowStatusReason() {
        const {coverage, coverageData} = this.props;
        const COVERAGE_CANCELLED_PREFIX = 'All coverages cancelled: ';
        const PLANNING_CANCELLED_PREFIX = 'Planning cancelled: ';
        let reason = get(coverageData, `workflow_status_reason[${coverage.coverage_id}]`);

        if (!get(reason, 'length', 0)) {
            return '';
        } else if (reason.startsWith(COVERAGE_CANCELLED_PREFIX)) {
            reason = reason.substring(COVERAGE_CANCELLED_PREFIX.length);
            reason = gettext('All coverages cancelled: {{ reason }}', {reason: reason});
        } else if (reason.startsWith(PLANNING_CANCELLED_PREFIX)) {
            reason = reason.substring(PLANNING_CANCELLED_PREFIX.length);
            reason = gettext('Planning cancelled: {{ reason }}', {reason: reason});
        }

        return reason;
    }

    render() {
        const coverage = this.props.coverage;
        const wireText = this.getItemText();
        const internalNote = get(this.props, 'coverageData.internal_note', {})[coverage.coverage_id];
        const edNote = this.state.wireItem ? this.state.wireItem.ednote :
            get(this.props, 'coverageData.ednote', {})[coverage.coverage_id];
        const reason = this.getWorkflowStatusReason();
        const scheduledStatus = get(this.props, 'coverageData.scheduled_update_status', {})[coverage.coverage_id];
        return (
            <Fragment>
                {wireText && (
                    <div className='coverage-item__row'>
                        <p className='wire-articles__item__text m-0'>{wireText}</p>
                    </div>
                )}

                {isCoverageBeingUpdated(coverage) && (
                    <div className='coverage-item__row'>
                        <span className='label label--blue'>{gettext('Update coming')}</span>
                    </div>
                )}

                <div className='coverage-item__row'>
                    <span key="topRow">
                        <span key="label" className='coverage-item__text-label me-1'>{gettext('status')}:</span>
                        <span key="value">{getCoverageStatusText(coverage)}</span>
                    </span>
                </div>

                {scheduledStatus && (
                    <div className='coverage-item__row'>
                        <span>{scheduledStatus}</span>
                    </div>
                )}

                {edNote && (
                    <div className='coverage-item__row'>
                        <AgendaEdNote item={{ednote: edNote}} noMargin />
                    </div>
                )}

                {reason && (
                    <div className='coverage-item__row'>
                        <AgendaEdNote item={{ednote: reason}} noMargin />
                    </div>
                )}

                {internalNote && (
                    <div className='coverage-item__row'>
                        <AgendaInternalNote internalNote={internalNote} noMargin />
                    </div>
                )}

                <div className='coverage-item__row d-flex justify-content-end gap-2'>
                    {this.getCoverageActions(coverage)}
                </div>
            </Fragment>
        );
    }
}

CoverageItemStatus.propTypes = {
    item: PropTypes.object,
    coverage: PropTypes.object,
    coverageData: PropTypes.object,
    wireItems: PropTypes.array,
    actions: PropTypes.array,
    user: PropTypes.string,
    internal_notes: PropTypes.object,
    ednotes: PropTypes.object,
    workflowStatusReasons: PropTypes.object,
    hideViewContentItems: PropTypes.array,
    contentLinkTarget: PropTypes.string,
};

CoverageItemStatus.defaultProps = {actions: []};
