import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {selectDashboard} from './actions';
import {dashboardPropType} from './types';

function DashboardSwitch({dashboards, activeDashboard, selectDashboard}) {
    if (get(dashboards, 'length', 0) <= 1) {
        // don't render the switch if configure dashboards is one
        return null;
    }

    return (
        <div className="toggle-button__group toggle-button__group--navbar ms-0 me-3">
            {dashboards.map((dashboard) => (
                <button key={dashboard._id}
                    className={'toggle-button' + (dashboard._id === activeDashboard ? ' toggle-button--active' : '')}
                    onClick={() => selectDashboard(dashboard._id)}
                >{dashboard.name}</button>
            ))}
        </div>
    );
}

DashboardSwitch.propTypes = {
    dashboards: dashboardPropType,
    activeDashboard: PropTypes.string,

    selectDashboard: PropTypes.func.isRequired,
};

const mapDispatchToProps = {
    selectDashboard,
};

export default connect(null, mapDispatchToProps)(DashboardSwitch);