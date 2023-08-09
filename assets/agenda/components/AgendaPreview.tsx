import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get} from 'lodash';

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

class AgendaPreview extends React.PureComponent<any, any> {
    static propTypes: any;
    static defaultProps: any;
    preview: any;
    constructor(props: any) {
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
        } = this.props;

        const isWatching = get(item, 'watches', []).includes(user);

        const previewClassName = classNames('wire-column__preview', {
            'wire-column__preview--covering': hasCoverages(item),
            'wire-column__preview--not-covering': !hasCoverages(item),
            'wire-column__preview--postponed': isPostponed(item),
            'wire-column__preview--rescheduled': isRescheduled(item),
            'wire-column__preview--open': !!item,
            'wire-column__preview--watched': isWatching,
        });

        const plan = (get(item, 'planning_items') || []).find((p: any) => p.guid === previewPlan);
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
                        <AgendaName item={item} />
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
                            mt2={!!(item.ednote || get(plan, 'ednote') || item.state_reason)} />
                        {!eventsOnly && <AgendaCoverageRequest item={item} requestCoverage={requestCoverage}/>}
                    </div>
                </Preview>
            </div>
        );
    }
}

AgendaPreview.propTypes = {
    user: PropTypes.string,
    item: PropTypes.object,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        action: PropTypes.func,
        url: PropTypes.func,
    })),
    followEvent: PropTypes.func,
    closePreview: PropTypes.func,
    openItemDetails: PropTypes.func,
    requestCoverage: PropTypes.func,
    previewGroup: PropTypes.string,
    previewPlan: PropTypes.string,
    eventsOnly: PropTypes.bool,
    wireItems: PropTypes.array,
    coverageActions: PropTypes.array,
    previewConfig: PropTypes.object,
    restrictCoverageInfo: PropTypes.bool,
};

AgendaPreview.defaultProps = {eventsOnly: false};

export default AgendaPreview;
