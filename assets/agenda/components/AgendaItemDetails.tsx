import React from 'react';
import {isEmpty, get} from 'lodash';

import {IAgendaItem, IArticle, ICoverageItemAction, IItemAction, IPreviewConfig, IUser} from 'interfaces';
import {gettext} from 'utils';

import {getLocations, mapsKey} from 'maps/utils';
import {hasAttachments, getInternalNote, planHasEvent} from '../utils';

import StaticMap from 'maps/components/static';
import PreviewActionButtons from 'components/PreviewActionButtons';

import Content from 'ui/components/Content';
import ContentBar from 'ui/components/ContentBar';
import ContentHeader from 'ui/components/ContentHeader';

import Article from 'ui/components/Article';
import ArticleBody from 'ui/components/ArticleBody';
import ArticleSidebar from 'ui/components/ArticleSidebar';
import ArticleSidebarBox from 'ui/components/ArticleSidebarBox';

import AgendaLongDescription from './AgendaLongDescription';
import AgendaMeta from './AgendaMeta';
import AgendaEdNote from './AgendaEdNote';
import AgendaInternalNote from './AgendaInternalNote';
import AgendaAttachments from './AgendaAttachments';
import AgendaCoverageRequest from './AgendaCoverageRequest';
import AgendaTags from './AgendaTags';
import {AgendaPreviewPlanning} from './AgendaPreviewPlanning';
import {AgendaPreviewEvent} from './AgendaPreviewEvent';
import {AgendaRegistrationInvitationDetails} from './AgendaRegistrationInvitationDetails';

interface IProps {
    item: IAgendaItem;
    planningId?: IAgendaItem['_id'];
    user: IUser['_id'];
    actions?: Array<IItemAction>;
    group?: string;
    eventsOnly?: boolean;
    wireItems?: Array<IArticle>;
    coverageActions?: Array<ICoverageItemAction>;
    detailsConfig: IPreviewConfig;
    restrictCoverageInfo?: boolean;
    onClose?(): void;
    requestCoverage(item: IAgendaItem, message: string): void;
}

function AgendaItemDetails(
    {
        item,
        user,
        actions,
        onClose,
        requestCoverage,
        group,
        planningId,
        eventsOnly,
        wireItems,
        coverageActions,
        detailsConfig,
        restrictCoverageInfo,
    }: IProps)
{
    const locations = getLocations(item);
    let map = null;

    // Ta: disabling the embedded map for now for ticket SDAN-334
    // const geoLocations = getGeoLocations(locations);
    // if (mapsLoaded() && !isEmpty(geoLocations)) {
    //     map = <Map locations={geoLocations} />;
    // }

    if (!map && mapsKey() && !isEmpty(locations)) {
        map = <StaticMap locations={locations} scale={2} />;
    }

    const plan = (get(item, 'planning_items') || []).find((p: any) => p.guid === planningId);
    const internalNotes = getInternalNote(item, plan);

    return (
        <Content type="item-detail">
            <ContentHeader>
                <ContentBar onClose={onClose}>
                    <PreviewActionButtons item={item} user={user} actions={actions}/>
                </ContentBar>
            </ContentHeader>

            <Article
                image={map}
                item={item}
                group={group}
                disableTextSelection={detailsConfig.disable_text_selection}
                detailsConfig={detailsConfig}
            >
                <ArticleBody>
                    <AgendaMeta item={item} />
                    <AgendaLongDescription item={item} plan={plan}/>
                    <AgendaRegistrationInvitationDetails item={item} />
                </ArticleBody>
                <ArticleSidebar>
                    <AgendaPreviewPlanning
                        user={user}
                        item={item}
                        planningId={planningId}
                        wireItems={wireItems}
                        coverageActions={coverageActions}
                        restrictCoverageInfo={restrictCoverageInfo}
                        previewConfig={detailsConfig}
                    />
                    {!planHasEvent(item) ? null : (
                        <AgendaPreviewEvent item={item} />
                    )}
                    {hasAttachments(item) && (
                        <ArticleSidebarBox label={gettext('Attachments')}>
                            <AgendaAttachments item={item} />
                        </ArticleSidebarBox>
                    )}
                    <AgendaTags
                        item={item}
                        plan={plan}
                        isItemDetail={true}
                        displayConfig={detailsConfig}
                    />
                    <AgendaEdNote item={item} plan={plan} secondaryNoteField='state_reason'/>
                    <AgendaInternalNote internalNote={internalNotes}
                        mt2={!!(item.ednote || get(plan, 'ednote') || item.state_reason)}/>
                    {!eventsOnly && <AgendaCoverageRequest item={item} requestCoverage={requestCoverage}/>}
                </ArticleSidebar>
            </Article>
        </Content>
    );
}

const component: React.ComponentType<any> = AgendaItemDetails;

export default component;
