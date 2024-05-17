import React from 'react';
import {connect} from 'react-redux';
import moment from 'moment-timezone';

import {IAgendaState, IArticle, ICoverageMetadataPreviewProps} from 'interfaces';

import {gettext, getConfig, COVERAGE_DATE_TIME_FORMAT} from 'utils';
import {isWatched, WORKFLOW_STATUS} from 'agenda/utils';
import {agendaContentLinkTarget} from 'ui/selectors';

import {CollapseBox} from 'ui/components/CollapseBox';
import ActionButton from 'components/ActionButton';
import {ToolTip} from 'ui/components/ToolTip';

interface IReduxStateProps {
    contentLinkTarget: string;
}

function getViewContentButtonAttributes(
    article: IArticle,
    viewContentEmail?: string
): React.AnchorHTMLAttributes<HTMLAnchorElement> {
    let title: string | undefined;
    let href: string | undefined;

    if (article._access === true) {
        title = gettext('Open in new tab');
        href = `/wire?item=${article._id}`;
    } else if (viewContentEmail != null) {
        title = gettext(
            'You don’t have access to this content, please contact {{email}}',
            {email: viewContentEmail}
        );
        href = `mailto:${viewContentEmail}`;
    } else {
        title = gettext('You don’t have access to this content');
    }

    return {href, title};
}

function CoverageActionsComponent({
    coverage,
    agenda,
    user,
    actions,
    wireItems,
    hideViewContentItems,
    contentLinkTarget,
}: ICoverageMetadataPreviewProps & IReduxStateProps) {
    const actionsToShow = (actions || []).filter((action) => (
        action.when == null ||
        action.when(coverage, user)
    ));
    const parentWatched = isWatched(agenda, user);
    const viewContentEmail = getConfig('view_content_tooltip_email');
    const actionButtons = actionsToShow.map((action) => (
        <ActionButton
            key={action.name}
            item={coverage}
            className="icon-button icon-button--small icon-button--bordered icon-button--tertiary ms-auto"
            action={{
                ...action,
                action: () => {
                    action.action(coverage, agenda);
                },
            }}
            plan={agenda}
            isVisited={parentWatched}
            disabled={parentWatched}
        />
    ));

    if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED &&
        ['video', 'video_explainer', 'picture', 'graphic'].includes(coverage.coverage_type) &&
        coverage.delivery_href != null
    ) {
        actionButtons.unshift(
            <ToolTip>
                <a
                    key="contentLink"
                    className="nh-button nh-button--small nh-button--tertiary"
                    title={gettext('Open in new tab')}
                    href={coverage.delivery_href}
                    target="_blank"
                    onClick={(e) => {
                        e.stopPropagation();
                    }}
                >
                    {gettext('View Content')}
                </a>
            </ToolTip>
        );
    }

    const wireIds = coverage.workflow_status !== WORKFLOW_STATUS.COMPLETED ?
        [] :
        (coverage.deliveries || [])
            .map((delivery) => delivery.delivery_id || '')
            .filter((wireId) => wireId.length > 0 && !(hideViewContentItems || []).includes(wireId));
    const wireVersions = (wireItems || []).filter((item) => wireIds.includes(item._id));

    return wireVersions.length === 0 ? (
        <div className="coverage-item__row d-flex justify-content-end gap-2">
            {actionButtons}
        </div>
    ) : (
        <CollapseBox
            id={coverage.coverage_id + '-actions'}
            title={(open) => (open ?
                gettext('Hide all versions ({{count}})', {count: wireIds.length}) :
                gettext('Show all versions ({{count}})', {count: wireIds.length})
            )}
            initiallyOpen={true}
            className={(open) => 'coverage-item__extended-row' + (!open ? '' : ' pb-0')}
            headerButtons={actionButtons}
        >
            <div className="coverage-item__extended-row-items">
                {wireVersions.map((version) => (
                    <div
                        key={version._id}
                        className="coverage-item__extended-row-item"
                    >
                        <div>
                            <span className="coverage-item__text-label me-1">
                                {gettext('Headline')}
                            </span>
                            <span>
                                {version.headline}
                            </span>
                        </div>
                        <div>
                            <span className="coverage-item__text-label me-1">
                                {gettext('Published')}
                            </span>
                            <span>
                                {moment(version.versioncreated).format(COVERAGE_DATE_TIME_FORMAT)}
                            </span>
                        </div>
                        <div className="ms-auto">
                            <ToolTip>
                                <a
                                    className="nh-button nh-button--small nh-button--tertiary"
                                    target={contentLinkTarget}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                    }}
                                    {...getViewContentButtonAttributes(version, viewContentEmail)}
                                >
                                    {gettext('View Content')}
                                </a>
                            </ToolTip>
                        </div>
                    </div>
                ))}
            </div>
        </CollapseBox>
    );
}

const mapStateToProps = (state: IAgendaState): IReduxStateProps => ({
    contentLinkTarget: agendaContentLinkTarget(state),
});

export const CoverageActions = connect<
    IReduxStateProps,
    {},
    ICoverageMetadataPreviewProps,
    IAgendaState
>(mapStateToProps)(CoverageActionsComponent);
