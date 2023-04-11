import React from 'react';
import {isEmpty, get} from 'lodash';
import {hasAttachments, getInternalNote, planHasEvent} from '../utils';
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
import {getLocations, mapsKey} from 'assets/maps/utils';
import StaticMap from 'assets/maps/components/static';
import Content from 'assets/ui/components/Content';
import ContentHeader from 'assets/ui/components/ContentHeader';
import ContentBar from 'assets/ui/components/ContentBar';
import PreviewActionButtons from 'assets/components/PreviewActionButtons';
import Article from 'assets/ui/components/Article';
import ArticleBody from 'assets/ui/components/ArticleBody';
import ArticleSidebar from 'assets/ui/components/ArticleSidebar';
import ArticleSidebarBox from 'assets/ui/components/ArticleSidebarBox';
import {gettext} from 'assets/utils';

interface IProps {
    item: any;
    user: any;
    actions: Array<{name: string, action: any, url: any}>;
    onClose: any;
    requestCoverage: any;
    group: string;
    planningId: string;
    eventsOnly: boolean;
    wireItems: Array<any>;
    coverageActions: Array<any>;
    detailsConfig: any;
    restrictCoverageInfo: boolean;
}

export default function AgendaItemDetails({
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
}: IProps) {
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
                    <AgendaInternalNote
                        internalNote={internalNotes}
                        mt2={!!(item.ednote || get(plan, 'ednote') || item.state_reason)}
                        onlyIcon={false}
                        noMargin={false}
                    />
                    {!eventsOnly && <AgendaCoverageRequest item={item} requestCoverage={requestCoverage}/>}
                </ArticleSidebar>
            </Article>
        </Content>
    );
}
