import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {uniqBy, get} from 'lodash';

import {gettext, isDisplayed} from 'utils';
import {filterGroupsToLabelMap} from 'search/selectors';

import InfoBox from './InfoBox';
import PreviewTagsBlock from './PreviewTagsBlock';
import PreviewTagsLink from './PreviewTagsLink';
import ArticleSlugline from 'ui/components/ArticleSlugline';


function formatCV(items, field) {
    return items && uniqBy(items, (item) => item.code).map((item) => (
        <PreviewTagsLink key={item.code}
            href={'/wire?filter=' + encodeURIComponent(JSON.stringify({[field]: [item.name]}))}
            text={item.name}
        />
    ));
}

function PreviewTagsComponent({item, isItemDetail, displayConfig, filterGroupLabels}) {
    const genres = item.genre && formatCV(item.genre, 'genre');
    const services = item.service && formatCV(item.service, 'service');
    const subjects = item.subject && formatCV(item.subject, 'subject');

    return (
        <InfoBox label={isItemDetail ? gettext('Metadata') : null} top={!isItemDetail}>
            {isDisplayed('slugline', displayConfig) && (
                <PreviewTagsBlock label={gettext('Slugline')}>
                    <ArticleSlugline item={item}/>
                </PreviewTagsBlock>)}

            {services && isDisplayed('services', displayConfig) &&
                <PreviewTagsBlock label={get(filterGroupLabels, 'service', gettext('Category'))}>
                    {services}
                </PreviewTagsBlock>
            }

            {subjects && isDisplayed('subjects', displayConfig) &&
                <PreviewTagsBlock label={get(filterGroupLabels, 'subject', gettext('Subject'))}>
                    {subjects}
                </PreviewTagsBlock>
            }

            {genres && isDisplayed('genre', displayConfig) &&
                <PreviewTagsBlock label={get(filterGroupLabels, 'genre', gettext('Content Type'))}>
                    {genres}
                </PreviewTagsBlock>
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

const mapStateToProps = (state) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
})

const PreviewTags = connect(mapStateToProps)(PreviewTagsComponent);

export default PreviewTags;
