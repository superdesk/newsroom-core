import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {uniqBy, get} from 'lodash';

import {gettext, isDisplayed} from 'utils';
import {filterGroupsToLabelMap} from 'search/selectors';

import InfoBox from 'wire/components/InfoBox';
import PreviewTagsBlock from 'wire/components/PreviewTagsBlock';
import PreviewTagsLink from 'wire/components/PreviewTagsLink';
import {getSubjects} from '../utils';

function formatCV(items, field) {
    return items && uniqBy(items, 'code').map((item) => (
        <PreviewTagsLink
            key={item.code}
            href={'/agenda?filter=' + encodeURIComponent(JSON.stringify({[field]: [item.name]}))}
            text={item.name}
        />
    ));
}

function AgendaTagsComponent({item, plan, isItemDetail, displayConfig, filterGroupLabels}) {
    const services = isDisplayed('services', displayConfig) &&
        formatCV([...(get(item, 'service') || []), ...(get(plan, 'service') || [])], 'service');
    const subjects = isDisplayed('subjects', displayConfig) &&
        formatCV([...getSubjects(item), ...getSubjects(plan)], 'subject');

    if (!subjects && !services) {
        return null;
    }

    return (
        <InfoBox
            label={isItemDetail ? gettext('Metadata') : null}
            top={!isItemDetail}
        >
            {!services ? null : (
                <PreviewTagsBlock label={get(filterGroupLabels, 'service', gettext('Category'))}>
                    {services}
                </PreviewTagsBlock>
            )}
            {!subjects ? null : (
                <PreviewTagsBlock label={get(filterGroupLabels, 'subject', gettext('Subject'))}>
                    {subjects}
                </PreviewTagsBlock>
            )}
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

const mapStateToProps = (state) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
});

const AgendaTags = connect(mapStateToProps)(AgendaTagsComponent);

export default AgendaTags;
