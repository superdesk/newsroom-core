import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';
import {gettext, isDisplayed} from 'utils';
import {filterGroupsToLabelMap} from 'search/selectors';
import InfoBox from './InfoBox';
import PreviewTagsBlock from './PreviewTagsBlock';
import {PreviewTagsSubjects} from './PreviewTagsSubjects';
import {PreviewTagsLinkList} from './PreviewTagsLinkList';
import ArticleSlugline from 'ui/components/ArticleSlugline';

function PreviewTagsComponent({item, isItemDetail, displayConfig, filterGroupLabels}: any) {
    const metadataFields = [];

    if (isDisplayed('slugline', displayConfig)) {
        metadataFields.push(
            <PreviewTagsBlock label={gettext('Slugline')}>
                <ArticleSlugline item={item}/>
            </PreviewTagsBlock>
        );
    }

    if ((isDisplayed('services', displayConfig) && item.service != null)) {
        metadataFields.push(
            <PreviewTagsBlock label={get(filterGroupLabels, 'service', gettext('Category'))}>
                <PreviewTagsLinkList
                    urlPrefix="/wire?filter="
                    items={item.service}
                    field="service"
                />
            </PreviewTagsBlock>
        );
    }

    if ((isDisplayed('genre', displayConfig) && item.genre != null)) {
        metadataFields.push(
            <PreviewTagsBlock label={get(filterGroupLabels, 'genre', gettext('Content Type'))}>
                <PreviewTagsLinkList
                    urlPrefix="/wire?filter="
                    items={item.genre}
                    field="genre"
                />
            </PreviewTagsBlock>
        );
    }

    if (item.subject) {
        metadataFields.push(
            <PreviewTagsSubjects
                subjects={item.subject}
                displayConfig={displayConfig}
                urlPrefix="/wire?filter="
                filterGroupLabels={filterGroupLabels}
            />
        );
    }

    return (
        <InfoBox label={gettext('Metadata')} top={!isItemDetail}>
            {metadataFields.length
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

PreviewTagsComponent.propTypes = {
    item: PropTypes.object,
    isItemDetail: PropTypes.bool,
    displayConfig: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};

const mapStateToProps = (state: any) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
});

const PreviewTags: React.ComponentType<any> = connect(mapStateToProps)(PreviewTagsComponent);

export default PreviewTags;
