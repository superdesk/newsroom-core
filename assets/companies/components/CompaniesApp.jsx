import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {newCompany, fetchCompanies} from '../actions';
import {setSearchQuery} from 'search/actions';
import {searchQuerySelector} from 'search/selectors';

import ListBar from 'components/ListBar';
import SearchResults from 'search/components/SearchResults';
import CompanyList from './CompanyList';
import EditCompany from './EditCompany';

function CompaniesApp({
    newCompany,
    setQuery,
    fetchCompanies,
    isLoading,
    activeQuery,
    totalCompanies,
    companyToEdit,
}) {
    return (
        <React.Fragment>
            <ListBar
                onNewItem={newCompany}
                setQuery={setQuery}
                fetch={fetchCompanies}
                buttonText={gettext('New Company')}
            />
            <div className="flex-row">
                {isLoading ? (
                    <div className="col d">
                        <div className="progress">
                            <div className="progress-bar" style={{width: '25%'}} />
                        </div>
                    </div>
                ) : (
                    <div className="flex-col flex-column">
                        {!activeQuery ? null : (
                            <SearchResults
                                totalItems={totalCompanies}
                                totalItemsLabel={activeQuery}
                            />
                        )}
                        <CompanyList />
                    </div>
                )}
                {!companyToEdit ? null : (
                    <EditCompany key={companyToEdit._id || '_new'} />
                )}
            </div>
        </React.Fragment>
    );
}

CompaniesApp.propTypes = {
    companyToEdit: PropTypes.object,
    newCompany: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalCompanies: PropTypes.number,
    fetchCompanies: PropTypes.func,
    setQuery: PropTypes.func,
};

const mapStateToProps = (state) => ({
    isLoading: state.isLoading,
    totalCompanies: state.totalCompanies,
    activeQuery: searchQuerySelector(state),
    companyToEdit: state.companyToEdit,
});

const mapDispatchToProps = {
    newCompany: newCompany,
    fetchCompanies: fetchCompanies,
    setQuery: setSearchQuery,
};

export default connect(mapStateToProps, mapDispatchToProps)(CompaniesApp);
