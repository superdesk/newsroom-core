import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';
import InfoBox from './InfoBox';
import PreviewTagsBlock from './PreviewTagsBlock';
import {PreviewTagsSubjects} from './PreviewTagsSubjects';
import {PreviewTagsLinkList} from './PreviewTagsLinkList';
import {filterGroupsToLabelMap} from 'assets/search/selectors';
import ArticleSlugline from 'assets/ui/components/ArticleSlugline';
import {isDisplayed, gettext} from 'assets/utils';


function PreviewTagsComponent({item, isItemDetail, displayConfig, filterGroupLabels}: any) {
    const services = !isDisplayed('services', displayConfig) ? null : (
        <PreviewTagsLinkList
            urlPrefix="/wire?filter="
            items={item.service}
            field="service"
        />
    );
    const genres = !isDisplayed('genre', displayConfig) ? null : (
        <PreviewTagsLinkList
            urlPrefix="/wire?filter="
            items={item.genre}
            field="genre"
        />
    );

    return (
        <InfoBox label={isItemDetail ? gettext('Metadata') : null} top={!isItemDetail}>
            {isDisplayed('slugline', displayConfig) && (
                <PreviewTagsBlock label={gettext('Slugline')}>
                    <ArticleSlugline item={item}/>
                </PreviewTagsBlock>)}

            {!services ? null : (
                <PreviewTagsBlock label={get(filterGroupLabels, 'service', gettext('Category'))}>
                    {services}
                </PreviewTagsBlock>
            )}

            <PreviewTagsSubjects
                subjects={item.subject || []}
                displayConfig={displayConfig}
                urlPrefix="/wire?filter="
                filterGroupLabels={filterGroupLabels}
            />

            {!genres ? null : (
                <PreviewTagsBlock label={get(filterGroupLabels, 'genre', gettext('Content Type'))}>
                    {genres}
                </PreviewTagsBlock>
            )}
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

const PreviewTags = connect(mapStateToProps)(PreviewTagsComponent);

export default PreviewTags;
