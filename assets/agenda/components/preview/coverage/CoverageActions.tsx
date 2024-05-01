import * as React from 'react';
import {connect} from 'react-redux';

import {ICoverageMetadataPreviewProps} from 'interfaces';

import {gettext, getConfig} from 'utils';
import {isWatched, WORKFLOW_STATUS} from 'agenda/utils';
import {agendaContentLinkTarget} from 'ui/selectors';

import ActionButton from 'components/ActionButton';
import {ToolTip} from 'ui/components/ToolTip';

interface IReduxStateProps {
    contentLinkTarget: string;
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
    const content = [(
        <React.Fragment key="action_buttons">
            {actionsToShow.map((action) => (
                <ActionButton
                    key={action.name}
                    item={coverage}
                    className='icon-button icon-button--small icon-button--bordered icon-button--tertiary'
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
            ))}
        </React.Fragment>
    )];

    if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED &&
        ['video', 'video_explainer', 'picture', 'graphic'].includes(coverage.coverage_type) &&
        coverage.delivery_href != null
    ) {
        content.unshift(
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
    } else if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED) {
        const wireItem = coverage.delivery_id == null ? null : (wireItems || []).find(
            (content) => content._id === coverage.delivery_id
        );

        if (wireItem != null && !(hideViewContentItems || []).includes(wireItem._id)) {
            content.unshift(wireItem._access === true ? (
                <ToolTip>
                    <a
                        key="contentLink"
                        className='nh-button nh-button--small nh-button--tertiary'
                        title={gettext('Open in new tab')}
                        href={`/wire?item=${coverage.delivery_id}`}
                        target={contentLinkTarget}
                        onClick={(e) => {
                            e.stopPropagation();
                        }}
                    >
                        {gettext('View Content')}
                    </a>
                </ToolTip>
            ) : (
                <ToolTip>
                    <a
                        key="contentLink"
                        className='nh-button nh-button--small nh-button--tertiary'
                        href={viewContentEmail ? `mailto:${viewContentEmail}` : undefined}
                        target={contentLinkTarget}
                        title={viewContentEmail ?
                            gettext(
                                'You don’t have access to this content, please contact {{email}}',
                                {email: viewContentEmail}
                            ) :
                            gettext('You don’t have access to this content')
                        }
                        onClick={(e) => {
                            e.stopPropagation();
                        }}
                    >
                        {gettext('View Content')}
                    </a>
                </ToolTip>
            ));
        }
    }

    return (
        <div className='coverage-item__row d-flex justify-content-end gap-2'>
            {content}
        </div>
    );
}

const mapStateToProps = (state: any): IReduxStateProps => ({
    contentLinkTarget: agendaContentLinkTarget(state),
});

export const CoverageActions = connect<IReduxStateProps, {}, ICoverageMetadataPreviewProps>(mapStateToProps)(CoverageActionsComponent);
