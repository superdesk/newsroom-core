import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {gettext} from 'utils';
import {renderModal} from 'actions';
import {setSection as _setSection, setProductFilter as _setProductFilter} from '../actions';
import {CompanyDetailsProductRow} from './CompanyDetailsProductRow';
import {searchQuerySelector} from 'search/selectors';
import {companySectionListSelector, companyProductSeatsSelector, currentCompanySelector} from '../selectors';

function CompanyDetailsComponent({company, showSeatRequestModal, setSection, companySections, seats, query}) {
    const sections = companySections[company._id];
    const numSections = sections.length;

    return (
        <div>
            <h3 className="home-section-heading">{company.name}</h3>
            <table className="table table--hollow">
                <thead>
                    <tr>
                        <th>{gettext('Products')}</th>
                        <th>{gettext('Users')}</th>
                        <th colSpan={numSections}>{gettext('Description')}</th>
                    </tr>
                </thead>
                <tbody>
                    {sections.map((section) => (
                        <React.Fragment key={section._id}>
                            <tr colSpan={2 + numSections} className="subheading">
                                <td>{section.name}</td>
                            </tr>

                            {
                                (query === null ?
                                    Object.values(seats[company._id]).filter((seat) => seat.section === section._id) :
                                    Object.values(seats[company._id]).filter((seat) => seat.section === section._id && seat.name.toString().includes(query))
                                )
                                    .map((seat) => (

                                        <CompanyDetailsProductRow
                                            key={seat._id}
                                            seat={seat}
                                            showSeatRequestModal={showSeatRequestModal}
                                            onNameClicked={() => setSection('users', seat._id)}
                                        />
                                    ))}
                        </React.Fragment>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

CompanyDetailsComponent.propTypes = {
    company: PropTypes.object.isRequired,
    showSeatRequestModal: PropTypes.func,
    setSection: PropTypes.func,
    companySections: PropTypes.object,
    seats: PropTypes.object,
    query: PropTypes.string,
};

const mapStateToProps = (state) => ({
    company: currentCompanySelector(state),
    companySections: companySectionListSelector(state),
    seats: companyProductSeatsSelector(state),
    query: searchQuerySelector(state),
});

const mapDispatchToProps = (dispatch) => ({
    showSeatRequestModal: (productIds) => dispatch(renderModal('productSeatRequest', {productIds})),
    setSection: (sectionId, productId) => {
        dispatch(_setSection(sectionId));
        dispatch(_setProductFilter(productId));
    },
});

export const CompanyDetails = connect(mapStateToProps, mapDispatchToProps)(CompanyDetailsComponent);
