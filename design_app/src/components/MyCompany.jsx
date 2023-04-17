import React from 'react';

function MyCompany() {
    return (
        <div>
            <h3 className="home-section-heading">My Company</h3>
            <table className="table table--hollow">
                <thead>
                    <tr>
                        <th>Products</th>
                        <th>Users</th>
                        <th colspan="2">Description</th>                        
                    </tr>
                </thead>
                <tbody>
                    <tr colspan="4" className="subheading">
                        <td>Wire</td>
                    </tr>
                    <tr>
                        <td>Product one</td>
                        <td>16/30</td>
                        <td className="font-light">Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</td>
                        <td><button className="btn btn-sm btn-outline-light">Request more seats</button></td>
                    </tr>
                    <tr>
                        <td className="text-danger">Product two</td>
                        <td className="text-danger">30/30</td>
                        <td className="font-light">Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</td>
                        <td><button className="btn btn-sm btn-outline-light">Request more seats</button></td>
                    </tr>
                    <tr>
                        <td>Product three</td>
                        <td>16/30</td>
                        <td className="font-light">Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</td>
                        <td><button className="btn btn-sm btn-outline-light">Request more seats</button></td>
                    </tr>
                    <tr colspan="4" className="subheading">
                        <td>Agenda</td>
                    </tr>
                    <tr>
                        <td>Product one</td>
                        <td>16/30</td>
                        <td className="font-light">Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</td>
                        <td><button className="btn btn-sm btn-outline-light">Request more seats</button></td>
                    </tr>
                    <tr>
                        <td>Product two</td>
                        <td>16/30</td>
                        <td className="font-light">Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</td>
                        <td><button className="btn btn-sm btn-outline-light">Request more seats</button></td>
                    </tr>
                    <tr>
                        <td>Product three</td>
                        <td>16/30</td>
                        <td className="font-light">Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</td>
                        <td><button className="btn btn-sm btn-outline-light">Request more seats</button></td>
                    </tr>
                </tbody>
            </table>
        </div>
    )
}

export default MyCompany;