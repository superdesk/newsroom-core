import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {selectCompany} from '../actions';
import {companiesSubscriberIdEnabled} from 'ui/selectors';

import CompanyListItem from './CompanyListItem';


function CompanyList({companies, selectCompany, activeCompanyId, companyTypes, showSubscriberId}) {
    const list = companies.map((company) =>
        <CompanyListItem
            key={company._id}
            company={company}
            onClick={selectCompany}
            isActive={activeCompanyId===company._id}
            type={companyTypes.find((ctype) => ctype.id === company.company_type)}
            showSubscriberId={showSubscriberId}
        />
    );

    return (
        <section className="content-main">
            <div className="list-items-container">
                <table
                    className="table table-hover"
                    tabIndex='-1'
                    data-test-id="company-list"
                >
                    <thead>
                        <tr>
                            <th>{ gettext('Name') }</th>
                            <th>{ gettext('Type') }</th>
                            {showSubscriberId && <th>{ gettext('Superdesk Subscriber Id') }</th>}
                            <th>{ gettext('Account Manager') }</th>
                            <th>{ gettext('Status') }</th>
                            <th>{ gettext('Contact') }</th>
                            <th>{ gettext('Telephone') }</th>
                            <th>{ gettext('Country') }</th>
                            <th>{ gettext('Created On') }</th>
                            <th>{ gettext('Expires On') }</th>
                        </tr>
                    </thead>
                    <tbody>{list}</tbody>
                </table>
            </div>
        </section>
    );
}

CompanyList.propTypes = {
    companies: PropTypes.arrayOf(PropTypes.object).isRequired,
    activeCompanyId: PropTypes.string,
    companyTypes: PropTypes.array,
    showSubscriberId: PropTypes.bool,
    selectCompany: PropTypes.func.isRequired,
};

const mapStateToProps = (state: any) => ({
    companies: state.companies.map((id) => state.companiesById[id]),
    activeCompanyId: state.activeCompanyId,
    companyTypes: state.companyTypes,
    showSubscriberId: companiesSubscriberIdEnabled(state),
});

const mapDispatchToProps = {
    selectCompany: selectCompany,
};

export default connect(mapStateToProps, mapDispatchToProps)(CompanyList);
