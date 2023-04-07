import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get, keyBy} from 'lodash';

import {gettext, getCreatedSearchParamLabel} from 'utils';
import {filterGroupsToLabelMap, filterGroups} from 'search/selectors';

const TopicParameters = ({topic, navigations, locators, filterGroupLabels, filterGroupsMain}) => {
    const filters = get(topic, 'filter') || {};
    const navsById = keyBy(navigations, '_id');
    const navs = (get(topic, 'navigation') || [])
        .map((navId) => get(navsById, `[${navId}].name`));

    const created = getCreatedSearchParamLabel(get(topic, 'created') || {});
    const dateLabels = [];

    if (created.relative) {
        dateLabels.push(created.relative);
    } else {
        if (created.from) {
            dateLabels.push(gettext('From: {{date}}', {date: created.from}));
        }
        if (created.to) {
            dateLabels.push(gettext('To: {{date}}', {date: created.to}));
        }
    }

    const renderParam = (name, items) => get(items, 'length', 0) < 1 ? null : (
        <div className="info-box__content">
            <span className="wire-column__preview__tags__headline">
                {name}
            </span>
            {items.map((item) => (
                <span className="wire-column__preview__tag" key={item.toString().replace(/\s+/g, '_')}>
                    {item}
                </span>
            ))}
        </div>
    );

    const filterGroups = () => {
        return (
            <div>
                {filterGroupsMain.map((element) => renderParam(get(filterGroupLabels, element.field, element.label), filters[element.field]))}
            </div>
        );
    };

    const renderPlace = () => {
        if (get(filters, 'place.length', 0) < 1) {
            return null;
        }

        const getPlaceName = (placeId) => {
            let region = (Object.values(locators) || []).find((l) => l.name === placeId);
            return region ?
                (get(region, 'state') || get(region, 'country') || get(region, 'world_region')) :
                placeId;
        };
        const places = (get(filters, 'place') || []).map(getPlaceName);

        return renderParam(gettext('Place'), places);
    };

    return (
        <div className="my-topics__form-params ">
            {renderParam(gettext('Search'), get(topic, 'query') ? [topic.query] : [])}
            {renderParam(gettext('Date Created'), dateLabels)}
            {renderParam(gettext('Topics'), navs)}
            {filterGroups()}
            {renderPlace()}
            {renderParam(gettext('Calendar'), filters.calendar)}
            {renderParam(gettext('Coverage Type'), filters.coverage)}
            {renderParam(gettext('Coverage Status'), filters.coverage_status)}
            {renderParam(gettext('Location'), filters.location)}
        </div>
    );
};

TopicParameters.propTypes = {
    topic: PropTypes.object,
    navigations: PropTypes.arrayOf(PropTypes.object),
    locators: PropTypes.array,
    filterGroupLabels: PropTypes.object,
    filterGroupsMain: PropTypes.array
};

const mapStateToProps = (state) => ({
    locators: get(state, 'locators.items', []),
    filterGroupLabels: filterGroupsToLabelMap(state),
    filterGroupsMain: filterGroups(state),
});

export default connect(mapStateToProps, null)(TopicParameters);
