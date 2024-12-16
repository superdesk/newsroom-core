import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';
import {gettext, isDisplayed} from 'utils';
import {filterGroupsToLabelMap} from 'search/selectors';
import InfoBox from 'wire/components/InfoBox';
import PreviewTagsBlock from 'wire/components/PreviewTagsBlock';
import {PreviewTagsLinkList} from 'wire/components/PreviewTagsLinkList';
import {PreviewTagsSubjects} from 'wire/components/PreviewTagsSubjects';
import {getSubjects} from '../utils';

function AgendaTagsComponent({item, plan, isItemDetail, displayConfig, filterGroupLabels}: any) {
    const metadataFields = [];
    const subject = [...getSubjects(item), ...getSubjects(plan)];

    if ((isDisplayed('services', displayConfig) && item.service.length)) {
        metadataFields.push(
            <PreviewTagsBlock label={get(filterGroupLabels, 'service', gettext('Category'))}>
                <PreviewTagsLinkList
                    urlPrefix="/agenda?filter="
                    items={[...(get(item, 'service') || []), ...(get(plan, 'service') || [])]}
                    field="service"
                />
            </PreviewTagsBlock>
        );
    }

    if(subject.length) {
        metadataFields.push(
            <PreviewTagsSubjects
                subjects={subject}
                displayConfig={displayConfig}
                urlPrefix="/agenda?filter="
                filterGroupLabels={filterGroupLabels}
            />
        );
    }

    return (
        <InfoBox
            label={gettext('Metadata')}
            top={!isItemDetail}
        >
            {metadataFields.length > 0
                ? (
                    metadataFields.map((field, index) => <React.Fragment key={index}>{field}</React.Fragment>)
                )
                : (
                    <div className='nh-container nh-container--highlight'>
                        <p className='nh-container__text--small'>No available Metadata</p>
                    </div>
                )
            }
        </InfoBox>
    );
}

AgendaTagsComponent.propTypes = {
    item: PropTypes.object,
    plan: PropTypes.object,
    isItemDetail: PropTypes.bool,
    displayConfig: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};

const mapStateToProps = (state: any) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
});

const AgendaTags: React.ComponentType<any> = connect(mapStateToProps)(AgendaTagsComponent);

export default AgendaTags;
