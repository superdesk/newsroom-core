import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {gettext} from 'assets/utils';
import {renderModal} from 'actions';
import {setSection as _setSection, setProductFilter as _setProductFilter} from '../actions';
import {CompanyDetailsProductRow} from './CompanyDetailsProductRow';
import {searchQuerySelector} from 'search/selectors';
import {companySectionListSelector, companyProductSeatsSelector, currentCompanySelector} from '../selectors';

function CompanyDetailsComponent({company, showSeatRequestModal, setSection, companySections, products, query}) {
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
                                    Object.values(products[company._id]).filter((product) => product.section === section._id) :
                                    Object.values(products[company._id]).filter((product) =>
                                        product.section === section._id &&
                                      product.name.toString().toLowerCase().includes(query.toLowerCase())
                                    )
                                )
                                    .map((product) => (

                                        <CompanyDetailsProductRow
                                            key={product._id}
                                            seat={product}
                                            showSeatRequestModal={showSeatRequestModal}
                                            onNameClicked={() => setSection('users', product._id)}
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
    products: PropTypes.object,
    query: PropTypes.string,
};

const mapStateToProps = (state: any) => ({
    company: currentCompanySelector(state),
    companySections: companySectionListSelector(state),
    products: companyProductSeatsSelector(state),
    query: searchQuerySelector(state),
});

const mapDispatchToProps = (dispatch: any) => ({
    showSeatRequestModal: (productIds) => dispatch(renderModal('productSeatRequest', {productIds})),
    setSection: (sectionId, productId) => {
        dispatch(_setSection(sectionId));
        dispatch(_setProductFilter(productId));
    },
});

export const CompanyDetails = connect(mapStateToProps, mapDispatchToProps)(CompanyDetailsComponent);
