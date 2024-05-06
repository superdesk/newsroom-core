import React from 'react';
import classNames from 'classnames';

import {IAgendaItem, IArticle, ICoverageItemAction, IItemAction, IPreviewConfig, IUser} from 'interfaces';

import {isEqualItem} from 'wire/utils';
import {hasCoverages, isPostponed, isRescheduled, getInternalNote, planHasEvent} from '../utils';

import PreviewActionButtons from 'components/PreviewActionButtons';
import Preview from 'ui/components/Preview';
import AgendaName from './AgendaName';
import AgendaTime from './AgendaTime';
import AgendaMeta from './AgendaMeta';
import AgendaEdNote from './AgendaEdNote';
import AgendaInternalNote from './AgendaInternalNote';
import AgendaPreviewImage from './AgendaPreviewImage';
import AgendaLongDescription from './AgendaLongDescription';
import AgendaPreviewAttachments from './AgendaPreviewAttachments';
import AgendaCoverageRequest from './AgendaCoverageRequest';
import AgendaTags from './AgendaTags';
import AgendaListItemLabels from './AgendaListItemLabels';
import {AgendaPreviewPlanning} from './AgendaPreviewPlanning';
import {AgendaPreviewEvent} from './AgendaPreviewEvent';
import {AgendaRegistrationInvitationDetails} from './AgendaRegistrationInvitationDetails';
import TopStoryLabel from './TopStoryLabel';
import ToBeConfirmedLabel from './ToBeConfirmedLabel';
import {LabelGroup} from 'ui/components/LabelGroup';

interface IProps {
    item: IAgendaItem;
    user: IUser['_id'];
    actions?: Array<IItemAction>;
    closePreview(): void;
    openItemDetails(item: IAgendaItem): void;
    requestCoverage(item: IAgendaItem, message: string): void;
    previewGroup?: string;
    previewPlan?: IAgendaItem['_id'];
    eventsOnly?: boolean;
    wireItems?: Array<IArticle>;
    coverageActions?: Array<ICoverageItemAction>;
    previewConfig: IPreviewConfig;
    restrictCoverageInfo?: boolean;
}

class AgendaPreview extends React.PureComponent<IProps, {}> {
    preview: any;
    constructor(props: IProps) {
        super(props);
    }

    componentDidUpdate(nextProps: any) {
        if (!isEqualItem(nextProps.item, this.props.item) && this.props.item) {
            this.preview.scrollTop = 0; // reset scroll on change
        }
    }

    render() {
        if (!this.props.item) {
            return (
                <div className="wire-column__preview" />
            );
        }

        const {
            item,
            user,
            actions,
            openItemDetails,
            requestCoverage,
            previewGroup,
            previewPlan,
            eventsOnly,
            wireItems,
            coverageActions,
            restrictCoverageInfo,
            previewConfig,
        } = this.props;

        const isWatching = (item.watches || []).includes(user);

        const previewClassName = classNames('wire-column__preview', {
            'wire-column__preview--covering': hasCoverages(item),
            'wire-column__preview--not-covering': !hasCoverages(item),
            'wire-column__preview--postponed': isPostponed(item),
            'wire-column__preview--rescheduled': isRescheduled(item),
            'wire-column__preview--open': !!item,
            'wire-column__preview--watched': isWatching,
        });

        const plan = (item.planning_items || []).find((p) => p.guid === previewPlan);
        const previewInnerElement = (<AgendaListItemLabels item={item} />);

        return (
            <div className={previewClassName}>
                <Preview onCloseClick={this.props.closePreview} published={item.versioncreated} innerElements={previewInnerElement}>
                    <div className='wire-column__preview__top-bar'>
                        <PreviewActionButtons item={item} user={user} actions={actions} plan={previewPlan} group={previewGroup} />
                    </div>

                    <div
                        id='preview-article'
                        ref={(preview: any) => this.preview = preview}
                        className={classNames(
                            'wire-column__preview__content pt-0',
                            {noselect: this.props.previewConfig.disable_text_selection}
                        )}
                    >
                        <hgroup>
                            <LabelGroup>
                                <TopStoryLabel item={item} config={previewConfig} size='big' />
                                <ToBeConfirmedLabel item={item} size='big' />
                            </LabelGroup>
                            <AgendaName item={item} noMargin/>
                        </hgroup>
                        <AgendaTime item={item}>
                            <AgendaListItemLabels
                                item={item}
                            />
                        </AgendaTime>
                        <AgendaPreviewImage item={item} onClick={openItemDetails} />
                        <AgendaMeta item={item} />
                        <AgendaLongDescription item={item} plan={plan}/>
                        <AgendaRegistrationInvitationDetails item={item} />

                        <AgendaPreviewPlanning
                            user={user}
                            item={item}
                            planningId={previewPlan}
                            wireItems={wireItems}
                            coverageActions={coverageActions}
                            previewGroup={previewGroup}
                            restrictCoverageInfo={restrictCoverageInfo}
                            previewConfig={previewConfig}
                        />
                        {!planHasEvent(item) ? null : (
                            <AgendaPreviewEvent item={item} />
                        )}
                        <AgendaPreviewAttachments item={item} />
                        <AgendaTags
                            item={item}
                            plan={plan}
                            isItemDetail={false}
                            displayConfig={this.props.previewConfig}
                        />
                        <AgendaEdNote item={item} plan={{}} secondaryNoteField='state_reason' />
                        <AgendaInternalNote internalNote={getInternalNote(item, {})}
                            mt2={!!(item.ednote || plan?.ednote || item.state_reason)} />
                        {eventsOnly !== true && <AgendaCoverageRequest item={item} requestCoverage={requestCoverage}/>}
                    </div>
                </Preview>
            </div>
        );
    }
}

export default AgendaPreview;
